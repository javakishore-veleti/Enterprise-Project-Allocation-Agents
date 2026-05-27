package com.javakishore.epaa.reporting.services.impl;

import com.javakishore.epaa.reporting.common.PageResponse;
import com.javakishore.epaa.reporting.dao.ReportRepository;
import com.javakishore.epaa.reporting.entities.ReportEntity;
import com.javakishore.epaa.reporting.services.ReportNotFoundException;
import com.javakishore.epaa.reporting.services.ReportingService;
import com.javakishore.epaa.reporting.services.dto.CreateReportRequest;
import com.javakishore.epaa.reporting.services.dto.ListReportsRequest;
import com.javakishore.epaa.reporting.services.dto.ReportResponse;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class ReportingServiceImpl implements ReportingService {

    private final ReportRepository repository;

    public ReportingServiceImpl(ReportRepository repository) {
        this.repository = repository;
    }

    @Override
    public ReportResponse create(CreateReportRequest r) {
        ReportEntity e = new ReportEntity();
        e.setProjectId(r.getProjectId());
        e.setRunId(r.getRunId());
        e.setSummaryText(r.getSummaryText());
        e.setMetricsJson(r.getMetricsJson());
        return toResponse(repository.save(e));
    }

    @Override
    @Transactional(readOnly = true)
    public ReportResponse get(String id) {
        return repository.findById(id).map(this::toResponse)
                .orElseThrow(() -> new ReportNotFoundException(id));
    }

    @Override
    @Transactional(readOnly = true)
    public ReportResponse latestForProject(String projectId) {
        return repository.findFirstByProjectIdOrderByCreatedAtDesc(projectId).map(this::toResponse)
                .orElseThrow(() -> new ReportNotFoundException("project:" + projectId));
    }

    @Override
    @Transactional(readOnly = true)
    public PageResponse<ReportResponse> list(ListReportsRequest r) {
        int page = Math.max(r.getPage(), 1);
        Pageable pageable = PageRequest.of(page - 1, r.getPageSize(),
                Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<ReportEntity> result = (r.getProjectId() != null && !r.getProjectId().isBlank())
                ? repository.findByProjectId(r.getProjectId(), pageable)
                : repository.findAll(pageable);
        List<ReportResponse> items = result.getContent().stream().map(this::toResponse).toList();
        return PageResponse.<ReportResponse>builder()
                .items(items).page(page).pageSize(r.getPageSize())
                .total(result.getTotalElements()).pages(result.getTotalPages()).build();
    }

    private ReportResponse toResponse(ReportEntity e) {
        return ReportResponse.builder()
                .id(e.getId()).projectId(e.getProjectId()).runId(e.getRunId())
                .summaryText(e.getSummaryText()).metricsJson(e.getMetricsJson())
                .createdAt(e.getCreatedAt()).build();
    }
}
