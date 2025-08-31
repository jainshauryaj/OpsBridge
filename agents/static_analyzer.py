from typing import Dict, Any
def static_analyzer_node():
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        diff = state.get('diff','')
        issues = []
        if 'print(' in diff: issues.append('print statements found')
        if '0.0.0.0' in diff: issues.append('binding to 0.0.0.0 in diff')
        return {'review': {'issues': issues}, 'messages':[{'type':'ai','content':f'Static analysis: {len(issues)} findings'}]}
    return _run
