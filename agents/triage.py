from typing import Dict, Any
from agents.utils import safe_shell, parse_signals_from_log
def triage_node(llm):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        tail = safe_shell('tail -n 200 logs/toy-web.log', approve=True)
        signals = parse_signals_from_log(tail.get('stdout',''))
        summary = llm.invoke('Summarize key symptoms:\n' + '\n'.join([s['line'] for s in signals[-40:]]))
        return {'messages':[summary], 'signals':signals, 'round': state.get('round',0)+1}
    return _run
