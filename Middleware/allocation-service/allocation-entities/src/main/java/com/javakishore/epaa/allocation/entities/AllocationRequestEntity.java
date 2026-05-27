package com.javakishore.epaa.allocation.entities;

import com.javakishore.epaa.allocation.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/**
 * Local audit of allocation triggers. The actual allocations/agent_runs are
 * written by the Agents service; this records that this middleware invoked it.
 */
@Entity
@Table(name = "allocation_requests")
@Getter
@Setter
public class AllocationRequestEntity extends BaseEntity {

    @Column(name = "project_id", nullable = false, length = 36)
    private String projectId;

    @Column(name = "agent_run_id", length = 36)
    private String agentRunId;

    @Column(name = "status", length = 30)
    private String status;   // requested | success | failed

    @Column(name = "allocation_time_ms")
    private Integer allocationTimeMs;

    @Column(name = "error", columnDefinition = "text")
    private String error;
}
