import glob
from typing import Dict, Any, List
def runbook_node(llm, retriever):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        service = state.get('incident',{}).get('service','')
        sigs = ' '.join([s.get('line','') for s in (state.get('signals') or [])[-50:]])
        hits = retriever.search(f"{service} {sigs}", k=3)
        plan = [{'step':'Check health','cmd':'curl -s http://localhost:8080/health'},
                {'step':'Tail logs','cmd':'tail -n 100 logs/toy-web.log'},
                {'step':'Restart service','cmd':'bash scripts/restart-toy-web.sh','verify':'echo 200'}]
        msg = llm.invoke('Plan drafted from runbook hits.')
        return {'messages':[msg], 'plan': plan}
    return _run
