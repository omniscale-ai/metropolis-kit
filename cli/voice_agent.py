#!/usr/bin/env python3
"""Create or update the ElevenLabs voice agent that lets a reader talk to a map (level 3).

The agent knows the map from the compiler's knowledge-base export, speaks with the guide's voice,
and points at the map through client tools that mirror the viewer's actions (show, highlight,
open, view, tour). State (agent id, tool ids, knowledge-base doc id) lives next to the spec in
<narration.audio>/../agent.json, so a re-run updates the same agent instead of creating another.

    ELEVENLABS_API_KEY=... python3 -m cli.voice_agent --spec examples/explainopolis/02-city-spec.json
    python3 -m cli.voice_agent --spec ... --env-file ~/git/deckcast/.env

Standard library only, like the compiler. The key is read from the environment or the env file
and never printed.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from cli.compiler import export_kb, validate_spec

API = 'https://api.elevenlabs.io'

TOOLS = [
    {'name': 'show', 'description': 'Fly the camera to map objects and light only them. Use it whenever you talk '
     'about a specific object, district or road. Pass ids from the knowledge base, e.g. @spire-compiler.',
     'properties': {'refs': {'type': 'array', 'description': 'Object ids from the knowledge base',
                             'items': {'type': 'string', 'description': 'An object id such as @spire-compiler'}}},
     'required': ['refs']},
    {'name': 'highlight', 'description': 'Light map objects without moving the camera, e.g. to compare things already '
     'on screen. An empty list clears the highlight.',
     'properties': {'refs': {'type': 'array', 'description': 'Object ids from the knowledge base',
                             'items': {'type': 'string', 'description': 'An object id'}}},
     'required': ['refs']},
    {'name': 'open', 'description': "Open an object's card with its details, when the listener wants the specifics.",
     'properties': {'ref': {'type': 'string', 'description': 'One object id from the knowledge base'}},
     'required': ['ref']},
    {'name': 'view', 'description': "Switch the map between the 3D city and the simpler metro diagram. Use 'metro' "
     "when the listener finds the city too busy.",
     'properties': {'mode': {'type': 'string', 'description': "'city' or 'metro'", 'enum': ['city', 'metro']}},
     'required': ['mode']},
    {'name': 'tour', 'description': 'Jump to a stop of the guided tour (1-based), or 0 to close the tour card.',
     'properties': {'stop': {'type': 'integer', 'description': 'Tour stop number; 0 closes the tour'}},
     'required': ['stop']},
]

PROMPT = """# Who you are
You are {guide}, the guide of "{title}", an interactive map. {subtitle}
You talk with a visitor who is looking at the map right now. They can see the map move when you call your tools.

# How you answer
- Answer only from the knowledge base. Every object there has an id in backticks; ids start with @ (e.g. @spire-compiler) — pass them to the tools exactly as written.
- Keep answers short: two or three spoken sentences, then stop or ask whether to go deeper.
- Whenever you mention an object, district or road, call `show` with its id first, so the map points at it while you talk. Use `highlight` to compare things already on screen, `open` for details, `view` with 'metro' if the visitor finds the city busy, `tour` to jump to a tour stop.
- Never invent numbers, names or claims. If the knowledge base does not answer, say so plainly and show the closest object.
- The map marks honest limits (constraints) where they act; mention them when they matter instead of overselling.
- Speak naturally; never read ids aloud, they are for the tools only.
"""


def call(method, path, key, body=None):
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as err:
        sys.exit(f"[!] {method} {path}: HTTP {err.code} {err.read().decode('utf-8', 'replace')[:600]}")


def load_key(env_file):
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key and env_file and os.path.exists(os.path.expanduser(env_file)):
        for line in open(os.path.expanduser(env_file), encoding='utf-8'):
            if line.strip().startswith('ELEVENLABS_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('"\'')
    if not key:
        sys.exit('[!] Set ELEVENLABS_API_KEY or pass --env-file')
    return key


def tool_config(t):
    return {'tool_config': {'type': 'client', 'name': t['name'], 'description': t['description'],
                            'parameters': {'type': 'object', 'properties': t['properties'], 'required': t['required']},
                            'expects_response': False}}


def main():
    ap = argparse.ArgumentParser(description='Create or update the ElevenLabs agent for a map (level 3)')
    ap.add_argument('--spec', required=True)
    ap.add_argument('--env-file', help='File with ELEVENLABS_API_KEY=... (e.g. ~/git/deckcast/.env)')
    ap.add_argument('--llm', default='gemini-3-flash-preview')
    ap.add_argument('--origin', action='append', default=[],
                    help='Hostname allowed to start conversations (repeatable); none = any site')
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding='utf-8'))
    errors = validate_spec(spec)
    if errors:
        sys.exit('[!] Spec does not validate:\n    ' + '\n    '.join(errors))
    narr = spec.get('narration', {})
    guide_id = next(iter(narr.get('speakers', {})), None)
    if not guide_id:
        sys.exit('[!] The spec needs narration.speakers (the first speaker is the agent)')
    guide = narr['speakers'][guide_id]
    meta = spec.get('city_metadata', {})
    voice_dir = os.path.join(os.path.dirname(os.path.abspath(args.spec)), os.path.dirname(narr.get('audio', 'voice/audio')))
    os.makedirs(voice_dir, exist_ok=True)
    state_path = os.path.join(voice_dir, 'agent.json')
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    key = load_key(args.env_file)

    kb_text = export_kb(spec)
    with open(os.path.join(voice_dir, 'kb.md'), 'w', encoding='utf-8') as f:
        f.write(kb_text)
    kb_name = f"{meta.get('title', 'map').lower()}-kb.md"
    doc = call('POST', '/v1/convai/knowledge-base/text', key, {'text': kb_text, 'name': kb_name})
    print(f"[+] Knowledge base uploaded: {kb_name} ({len(kb_text.split())} words)")

    tool_ids = state.get('tool_ids', {})
    for t in TOOLS:
        if t['name'] in tool_ids:
            call('PATCH', f"/v1/convai/tools/{tool_ids[t['name']]}", key, tool_config(t))
        else:
            tool_ids[t['name']] = call('POST', '/v1/convai/tools', key, tool_config(t))['id']
    print(f"[+] Client tools: {', '.join(tool_ids)}")

    agent_cfg = {
        'name': f"{meta.get('title', 'Map').title()} — talk to the city",
        'conversation_config': {
            'agent': {
                'first_message': f"Hi, I'm {guide.get('name', 'your guide')}. Ask me anything about this map — "
                                 "how it was made, or what any building means — and I'll show you.",
                'language': narr.get('language', 'en'),
                'prompt': {
                    'prompt': PROMPT.format(guide=guide.get('name', 'the guide'), title=meta.get('title', 'the map'),
                                            subtitle=meta.get('subtitle', '')),
                    'llm': args.llm,
                    'temperature': 0.2,
                    'tool_ids': list(tool_ids.values()),
                    'knowledge_base': [{'type': 'text', 'name': kb_name, 'id': doc['id'], 'usage_mode': 'auto'}],
                },
            },
            'tts': {'voice_id': guide['voice']['voice_id'], 'model_id': 'eleven_v3_conversational'},
        },
        'platform_settings': {'auth': {'enable_auth': False,
                                       'allowlist': [{'hostname': h} for h in args.origin]}},
    }
    old_doc = state.get('kb_doc_id')
    if state.get('agent_id'):
        call('PATCH', f"/v1/convai/agents/{state['agent_id']}", key, agent_cfg)
        print(f"[+] Agent updated: {state['agent_id']}")
    else:
        state['agent_id'] = call('POST', '/v1/convai/agents/create', key, agent_cfg)['agent_id']
        print(f"[+] Agent created: {state['agent_id']}")
    if old_doc and old_doc != doc['id']:
        call('DELETE', f"/v1/convai/knowledge-base/{old_doc}", key)
    state.update({'tool_ids': tool_ids, 'kb_doc_id': doc['id'], 'kb_name': kb_name})
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
        f.write('\n')
    print(f"[✓] {state_path}")


if __name__ == '__main__':
    main()
