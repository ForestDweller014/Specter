from __future__ import annotations

import json
from pathlib import Path

from specter.courtroom.models import FeedbackTargetNode


class ActionGraphLoadError(ValueError):
    pass


class ActionGraphLoader:
    expected_schema = "dullahan.action_graph.v1"

    def load_targets(
        self,
        path: Path,
        *,
        include_unanswered_nodes: bool = False,
    ) -> tuple[dict, list[FeedbackTargetNode]]:
        graph = json.loads(path.read_text(encoding="utf-8"))
        if graph.get("schema") != self.expected_schema:
            raise ActionGraphLoadError(f"unsupported action graph schema: {graph.get('schema')!r}")

        nodes_by_id = {str(node.get("id", "")): node for node in graph.get("nodes", [])}
        children_by_source: dict[str, list[str]] = {}
        incoming_edge_by_target: dict[str, dict] = {}
        for edge in graph.get("edges", []):
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if source and target:
                children_by_source.setdefault(source, []).append(target)
                incoming_edge_by_target[target] = edge

        targets = []
        for node in graph.get("nodes", []):
            response = node.get("response")
            responses = node.get("responses") or []
            primary_response = response or (responses[0] if responses else None)
            expert_id = self._expert_id(primary_response)
            if expert_id is None and not include_unanswered_nodes:
                continue
            node_id = str(node["id"])
            incoming_edge = incoming_edge_by_target.get(node_id)
            parent_query_id = str(incoming_edge["source"]) if incoming_edge else None
            parent_node = nodes_by_id.get(parent_query_id or "")
            targets.append(
                FeedbackTargetNode(
                    query_id=node_id,
                    expert_id=expert_id or "expert:unassigned",
                    query=node.get("query") or {},
                    context=node.get("context"),
                    response=primary_response,
                    responses=responses,
                    child_query_ids=children_by_source.get(node_id, []),
                    child_query_texts=[
                        self._node_query_text(nodes_by_id.get(child_id))
                        for child_id in children_by_source.get(node_id, [])
                    ],
                    parent_query_id=parent_query_id,
                    parent_query_text=self._node_query_text(parent_node),
                    delegation_query=str(incoming_edge.get("query", "")) if incoming_edge else "",
                    depth=int(node.get("depth") or 0),
                    sender_id=str(node.get("sender_id") or ""),
                )
            )

        return graph, targets

    def _expert_id(self, response: dict | None) -> str | None:
        if not response:
            return None
        expert_id = response.get("expert_id")
        if expert_id is None:
            return None
        return str(expert_id)

    def _node_query_text(self, node: dict | None) -> str:
        if not node:
            return ""
        query = node.get("query") or {}
        return str(query.get("query", "")).strip()
