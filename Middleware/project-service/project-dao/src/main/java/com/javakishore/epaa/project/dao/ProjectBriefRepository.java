package com.javakishore.epaa.project.dao;

import com.javakishore.epaa.project.entities.ProjectBriefEntity;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProjectBriefRepository extends JpaRepository<ProjectBriefEntity, String> {

    Optional<ProjectBriefEntity> findFirstByProjectId(String projectId);
}
