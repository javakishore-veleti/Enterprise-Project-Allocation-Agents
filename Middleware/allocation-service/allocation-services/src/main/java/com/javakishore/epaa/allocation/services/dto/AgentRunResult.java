package com.javakishore.epaa.allocation.services.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Deserialised response from the Agents service POST /allocations/run. */
@Getter
@Setter
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class AgentRunResult {

    @JsonProperty("run_id")
    private String runId;

    @JsonProperty("project_id")
    private String projectId;

    private String status;

    @JsonProperty("allocation_time_ms")
    private Integer allocationTimeMs;

    private List<AssignmentDTO> assignments;

    private String report;

    private Map<String, Object> metrics;
}
