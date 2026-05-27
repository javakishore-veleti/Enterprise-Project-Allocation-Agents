package com.javakishore.epaa.project.api;

import com.javakishore.epaa.project.common.PageResponse;
import com.javakishore.epaa.project.services.ProjectService;
import com.javakishore.epaa.project.services.dto.CreateProjectRequest;
import com.javakishore.epaa.project.services.dto.ListProjectsRequest;
import com.javakishore.epaa.project.services.dto.ProjectResponse;
import com.javakishore.epaa.project.services.dto.UpdateProjectRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    private final ProjectService service;

    public ProjectController(ProjectService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProjectResponse create(@Valid @RequestBody CreateProjectRequest request) {
        return service.create(request);
    }

    @GetMapping("/{id}")
    public ProjectResponse get(@PathVariable String id) {
        return service.get(id);
    }

    @PutMapping("/{id}")
    public ProjectResponse update(@PathVariable String id, @Valid @RequestBody UpdateProjectRequest request) {
        request.setId(id);
        return service.update(request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        service.delete(id);
    }

    @GetMapping
    public PageResponse<ProjectResponse> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "15") int pageSize,
            @RequestParam(required = false) String search) {
        ListProjectsRequest request = new ListProjectsRequest();
        request.setPage(page);
        request.setPageSize(pageSize);
        request.setSearch(search);
        return service.list(request);
    }
}
