package com.javakishore.epaa.reporting.services;

import com.javakishore.epaa.reporting.common.PageResponse;
import com.javakishore.epaa.reporting.services.dto.CreateReportRequest;
import com.javakishore.epaa.reporting.services.dto.ListReportsRequest;
import com.javakishore.epaa.reporting.services.dto.ReportResponse;

public interface ReportingService {

    ReportResponse create(CreateReportRequest request);

    ReportResponse get(String id);

    ReportResponse latestForProject(String projectId);

    PageResponse<ReportResponse> list(ListReportsRequest request);
}
