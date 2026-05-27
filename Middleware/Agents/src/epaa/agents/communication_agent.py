"""Agent 5 — Communication. Queues a notification per assignee.

Notifications are written as rows (channel=log locally); notification-service
(M4) delivers them. We resolve the just-created Allocation ids for linkage.
"""
from __future__ import annotations

from sqlalchemy import select

from epaa_datalake.models import Allocation, Notification

from .base import BaseAgent, PipelineContext


class CommunicationAgent(BaseAgent):
    name = "communication"

    def run(self, session, ctx: PipelineContext) -> dict:
        session.flush()  # ensure allocations have ids
        alloc_by_emp = {
            a.employee_id: a.id
            for a in session.scalars(
                select(Allocation).where(Allocation.project_id == ctx.project_id,
                                         Allocation.status == "assigned")
            ).all()
        }
        count = 0
        for a in ctx.assignments:
            subject = f"You've been assigned to {ctx.project.name}"
            body = (
                f"Hi {a['full_name']},\n\nYou have been allocated to project "
                f"\"{ctx.project.name}\" ({ctx.project.client_name}) as a {a['title']}. "
                f"Match relevance {a['relevance']}, final score {a['final_score']}.\n\n"
                f"Reason: {a['rationale']}"
            )
            session.add(Notification(
                employee_id=a["employee_id"], allocation_id=alloc_by_emp.get(a["employee_id"]),
                channel="log", subject=subject, body=body, status="queued",
            ))
            count += 1

        ctx.notifications = count
        return {"notifications_queued": count}
