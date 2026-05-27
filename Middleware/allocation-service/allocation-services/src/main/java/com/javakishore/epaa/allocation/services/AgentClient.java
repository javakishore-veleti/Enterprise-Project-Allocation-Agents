package com.javakishore.epaa.allocation.services;

import com.javakishore.epaa.allocation.services.dto.AgentRunResult;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Thin client over the Agents (FastAPI) service. */
@Component
public class AgentClient {

    private final RestClient client;

    public AgentClient(@Value("${epaa.agents.base-url:http://localhost:8001}") String baseUrl) {
        this.client = RestClient.builder().baseUrl(baseUrl).build();
    }

    /** Trigger the 6-agent pipeline for a project. */
    public AgentRunResult runAllocation(String projectId) {
        return client.post()
                .uri("/allocations/run")
                .body(Map.of("project_id", projectId))
                .retrieve()
                .body(AgentRunResult.class);
    }
}
