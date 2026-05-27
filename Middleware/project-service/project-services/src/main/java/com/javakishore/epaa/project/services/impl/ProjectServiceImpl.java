package com.javakishore.epaa.project.services.impl;

import com.javakishore.epaa.project.common.PageResponse;
import com.javakishore.epaa.project.dao.ProjectBriefRepository;
import com.javakishore.epaa.project.dao.ProjectRepository;
import com.javakishore.epaa.project.entities.ProjectBriefEntity;
import com.javakishore.epaa.project.entities.ProjectEntity;
import com.javakishore.epaa.project.services.ProjectNotFoundException;
import com.javakishore.epaa.project.services.ProjectService;
import com.javakishore.epaa.project.services.dto.CreateProjectRequest;
import com.javakishore.epaa.project.services.dto.ListProjectsRequest;
import com.javakishore.epaa.project.services.dto.ProjectResponse;
import com.javakishore.epaa.project.services.dto.UpdateProjectRequest;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class ProjectServiceImpl implements ProjectService {

    private final ProjectRepository projects;
    private final ProjectBriefRepository briefs;

    public ProjectServiceImpl(ProjectRepository projects, ProjectBriefRepository briefs) {
        this.projects = projects;
        this.briefs = briefs;
    }

    @Override
    public ProjectResponse create(CreateProjectRequest r) {
        ProjectEntity p = new ProjectEntity();
        p.setName(r.getName());
        p.setClientName(r.getClientName());
        p.setPriority(r.getPriority());
        p.setComplexity(r.getComplexity());
        p.setDurationWeeks(r.getDurationWeeks());
        p.setRequiredHeadcount(r.getRequiredHeadcount());
        p.setStartDate(r.getStartDate());
        p.setStatus(r.getStatus() != null ? r.getStatus() : "open");
        p = projects.save(p);
        if (r.getBriefText() != null && !r.getBriefText().isBlank()) {
            upsertBrief(p.getId(), r.getBriefText());
        }
        return toResponse(p);
    }

    @Override
    @Transactional(readOnly = true)
    public ProjectResponse get(String id) {
        ProjectEntity p = projects.findById(id).orElseThrow(() -> new ProjectNotFoundException(id));
        return toResponse(p);
    }

    @Override
    public ProjectResponse update(UpdateProjectRequest r) {
        ProjectEntity p = projects.findById(r.getId())
                .orElseThrow(() -> new ProjectNotFoundException(r.getId()));
        if (r.getName() != null) p.setName(r.getName());
        if (r.getClientName() != null) p.setClientName(r.getClientName());
        if (r.getPriority() != null) p.setPriority(r.getPriority());
        if (r.getComplexity() != null) p.setComplexity(r.getComplexity());
        if (r.getDurationWeeks() != null) p.setDurationWeeks(r.getDurationWeeks());
        if (r.getRequiredHeadcount() != null) p.setRequiredHeadcount(r.getRequiredHeadcount());
        if (r.getStartDate() != null) p.setStartDate(r.getStartDate());
        if (r.getStatus() != null) p.setStatus(r.getStatus());
        p = projects.save(p);
        if (r.getBriefText() != null) {
            upsertBrief(p.getId(), r.getBriefText());
        }
        return toResponse(p);
    }

    @Override
    public void delete(String id) {
        if (!projects.existsById(id)) {
            throw new ProjectNotFoundException(id);
        }
        briefs.findFirstByProjectId(id).ifPresent(briefs::delete);
        projects.deleteById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public PageResponse<ProjectResponse> list(ListProjectsRequest r) {
        int page = Math.max(r.getPage(), 1);
        Pageable pageable = PageRequest.of(page - 1, r.getPageSize(),
                Sort.by(Sort.Direction.DESC, "createdAt"));
        String search = r.getSearch();
        Page<ProjectEntity> result = (search == null || search.isBlank())
                ? projects.findAll(pageable)
                : projects.findByNameContainingIgnoreCaseOrClientNameContainingIgnoreCase(
                        search, search, pageable);
        List<ProjectResponse> items = result.getContent().stream().map(this::toResponse).toList();
        return PageResponse.<ProjectResponse>builder()
                .items(items).page(page).pageSize(r.getPageSize())
                .total(result.getTotalElements()).pages(result.getTotalPages()).build();
    }

    private void upsertBrief(String projectId, String text) {
        ProjectBriefEntity b = briefs.findFirstByProjectId(projectId).orElseGet(ProjectBriefEntity::new);
        b.setProjectId(projectId);
        b.setBriefText(text);
        briefs.save(b);
    }

    private ProjectResponse toResponse(ProjectEntity p) {
        String briefText = briefs.findFirstByProjectId(p.getId())
                .map(ProjectBriefEntity::getBriefText).orElse(null);
        return ProjectResponse.builder()
                .id(p.getId()).name(p.getName()).clientName(p.getClientName())
                .priority(p.getPriority()).complexity(p.getComplexity())
                .durationWeeks(p.getDurationWeeks()).requiredHeadcount(p.getRequiredHeadcount())
                .startDate(p.getStartDate()).status(p.getStatus())
                .briefText(briefText).createdAt(p.getCreatedAt()).build();
    }
}
