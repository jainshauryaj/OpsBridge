from typing import Dict, Any
def style_guide_node(llm, retriever):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        hits = retriever.search('style rules for error handling logging rollout rollback', k=3)
        notes = llm.invoke('Write concise style notes with [S1]/[S2] citations based on snippets:\n'+str(hits))
        rv = state.get('review',{}); rv['style']=getattr(notes,'content',str(notes))
        return {'review': rv, 'messages':[notes]}
    return _run
