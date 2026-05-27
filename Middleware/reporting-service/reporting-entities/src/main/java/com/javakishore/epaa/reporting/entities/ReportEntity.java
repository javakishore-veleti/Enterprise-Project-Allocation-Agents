package com.javakishore.epaa.reporting.entities;

import com.javakishore.epaa.reporting.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/** Managerial report for an allocation run. metricsJson holds the paper's
 * metrics (allocation time, conflicts avoided, etc.) as a JSON string. */
@Entity
@Table(name = "reports")
@Getter
@Setter
public class ReportEntity extends BaseEntity {

    @Column(name = "project_id", nullable = false, length = 36)
    private String projectId;

    @Column(name = "run_id", length = 36)
    private String runId;

    @Column(name = "summary_text", columnDefinition = "text")
    private String summaryText;

    @Column(name = "metrics_json", columnDefinition = "text")
    private String metricsJson;
}
