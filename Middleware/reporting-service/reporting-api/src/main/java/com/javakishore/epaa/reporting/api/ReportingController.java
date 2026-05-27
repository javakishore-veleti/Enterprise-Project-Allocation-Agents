package com.javakishore.epaa.reporting.api;

import com.javakishore.epaa.reporting.common.PageResponse;
import com.javakishore.epaa.reporting.services.ReportingService;
import com.javakishore.epaa.reporting.services.dto.CreateReportRequest;
import com.javakishore.epaa.reporting.services.dto.ListReportsRequest;
import com.javakishore.epaa.reporting.services.dto.ReportResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/reports")
public class ReportingController {

    private final ReportingService service;

    public ReportingController(ReportingService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ReportResponse create(@Valid @RequestBody CreateReportRequest request) {
        return service.create(request);
    }

    @GetMapping("/{id}")
    public ReportResponse get(@PathVariable String id) {
        return service.get(id);
    }

    @GetMapping("/project/{projectId}/latest")
    public ReportResponse latest(@PathVariable String projectId) {
        return service.latestForProject(projectId);
    }

    @GetMapping
    public PageResponse<ReportResponse> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "15") int pageSize,
            @RequestParam(required = false) String projectId) {
        ListReportsRequest request = new ListReportsRequest();
        request.setPage(page);
        request.setPageSize(pageSize);
        request.setProjectId(projectId);
        return service.list(request);
    }
}
