package com.javakishore.epaa.project.dao;

import com.javakishore.epaa.project.entities.ProjectEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProjectRepository extends JpaRepository<ProjectEntity, String> {

    Page<ProjectEntity> findByNameContainingIgnoreCaseOrClientNameContainingIgnoreCase(
            String name, String clientName, Pageable pageable);
}
