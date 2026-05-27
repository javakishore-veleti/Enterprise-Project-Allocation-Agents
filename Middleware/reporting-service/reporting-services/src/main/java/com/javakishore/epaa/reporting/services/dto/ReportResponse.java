package com.javakishore.epaa.reporting.services.dto;

import com.javakishore.epaa.reporting.common.BaseResponse;
import java.time.OffsetDateTime;
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
public class ReportResponse extends BaseResponse {
    private String id;
    private String projectId;
    private String runId;
    private String summaryText;
    private String metricsJson;
    private OffsetDateTime createdAt;
}
