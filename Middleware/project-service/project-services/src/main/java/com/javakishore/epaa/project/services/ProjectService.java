package com.javakishore.epaa.project.services;

import com.javakishore.epaa.project.common.PageResponse;
import com.javakishore.epaa.project.services.dto.CreateProjectRequest;
import com.javakishore.epaa.project.services.dto.ListProjectsRequest;
import com.javakishore.epaa.project.services.dto.ProjectResponse;
import com.javakishore.epaa.project.services.dto.UpdateProjectRequest;

public interface ProjectService {

    ProjectResponse create(CreateProjectRequest request);

    ProjectResponse get(String id);

    ProjectResponse update(UpdateProjectRequest request);

    void delete(String id);

    PageResponse<ProjectResponse> list(ListProjectsRequest request);
}
