package com.javakishore.epaa.allocation.services.impl;

import com.javakishore.epaa.allocation.dao.AllocationRequestRepository;
import com.javakishore.epaa.allocation.entities.AllocationRequestEntity;
import com.javakishore.epaa.allocation.services.AgentClient;
import com.javakishore.epaa.allocation.services.AllocationFailedException;
import com.javakishore.epaa.allocation.services.AllocationService;
import com.javakishore.epaa.allocation.services.dto.AgentRunResult;
import com.javakishore.epaa.allocation.services.dto.AllocationRunResponse;
import com.javakishore.epaa.allocation.services.dto.RunAllocationRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AllocationServiceImpl implements AllocationService {

    private final AgentClient agentClient;
    private final AllocationRequestRepository requests;

    public AllocationServiceImpl(AgentClient agentClient, AllocationRequestRepository requests) {
        this.agentClient = agentClient;
        this.requests = requests;
    }

    @Override
    @Transactional
    public AllocationRunResponse run(RunAllocationRequest request) {
        AllocationRequestEntity audit = new AllocationRequestEntity();
        audit.setProjectId(request.getProjectId());
        audit.setStatus("requested");
        audit = requests.save(audit);

        try {
            AgentRunResult result = agentClient.runAllocation(request.getProjectId());
            audit.setAgentRunId(result.getRunId());
            audit.setStatus(result.getStatus() != null ? result.getStatus() : "success");
            audit.setAllocationTimeMs(result.getAllocationTimeMs());
            requests.save(audit);

            return AllocationRunResponse.builder()
                    .requestId(audit.getId())
                    .runId(result.getRunId())
                    .projectId(result.getProjectId())
                    .status(audit.getStatus())
                    .allocationTimeMs(result.getAllocationTimeMs())
                    .assignments(result.getAssignments())
                    .report(result.getReport())
                    .build();
        } catch (RuntimeException ex) {
            audit.setStatus("failed");
            audit.setError(ex.getMessage());
            requests.save(audit);
            throw new AllocationFailedException("Agents service call failed", ex);
        }
    }
}
