package com.javakishore.epaa.reporting.services.dto;

import com.javakishore.epaa.reporting.common.BaseRequest;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class CreateReportRequest extends BaseRequest {

    @NotBlank
    private String projectId;

    private String runId;
    private String summaryText;
    private String metricsJson;
}
