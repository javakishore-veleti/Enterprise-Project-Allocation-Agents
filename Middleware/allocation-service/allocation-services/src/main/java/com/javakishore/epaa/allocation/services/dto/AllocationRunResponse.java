package com.javakishore.epaa.allocation.services.dto;

import com.javakishore.epaa.allocation.common.BaseResponse;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AllocationRunResponse extends BaseResponse {
    private String requestId;          // local audit id
    private String runId;              // Agents agent_run id
    private String projectId;
    private String status;
    private Integer allocationTimeMs;
    private List<AssignmentDTO> assignments;
    private String report;
}
