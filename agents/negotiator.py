from typing import Dict, Any
def negotiator_node(llm):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        rv = state.get('review',{})
        decision = 'revert' if len(rv.get('issues',[]))>0 else 'no_code_issue'
        rv['decision']=decision; rv['reason']='Heuristic decision based on issues count'
        plan = state.get('plan') or []
        if decision=='revert':
            plan = [{'step':'Revert recent change (demo placeholder)','cmd':'systemctl restart toy-web','verify':'curl -s http://localhost:8080/health'}] + plan
        return {'review':rv, 'plan':plan, 'messages':[{'type':'ai','content':f'Decision: {decision}'}]}
    return _run
