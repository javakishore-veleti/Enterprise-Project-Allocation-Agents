package com.javakishore.epaa.reporting.dao;

import com.javakishore.epaa.reporting.entities.ReportEntity;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ReportRepository extends JpaRepository<ReportEntity, String> {

    Page<ReportEntity> findByProjectId(String projectId, Pageable pageable);

    Optional<ReportEntity> findFirstByProjectIdOrderByCreatedAtDesc(String projectId);
}
