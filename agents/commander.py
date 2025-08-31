from typing import Dict, Any, List
from agents.utils import safe_shell, write_incident
def commander_node(approve: bool=False):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = state.get('plan') or []
        actions: List[Dict[str, Any]] = state.get('actions') or []
        if not state.get('approvals',{}).get('approved') and not approve:
            cmds = [p['cmd'] for p in plan if p.get('cmd')]
            return {'messages':[{'type':'ai','content':'Proposed commands:\n'+'\n'.join(cmds)}], 'actions': actions, 'done': False}
        for step in plan:
            record = {'step': step}
            if step.get('cmd'):
                out = safe_shell(step['cmd'], approve=approve); record['out']=out
                if step.get('verify'):
                    v = safe_shell(step['verify'], approve=approve); record['verify']=v
            actions.append(record)
        resolved = any('200' in (a.get('verify',{}).get('stdout') or '') for a in actions)
        tmp = dict(state); tmp['actions']=actions
        p = write_incident(tmp)
        return {'actions': actions, 'done': resolved, 'messages':[{'type':'ai','content':f'Report: {p}'}]}
    return _run
