package com.javakishore.epaa.allocation.dao;

import com.javakishore.epaa.allocation.entities.AllocationRequestEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AllocationRequestRepository extends JpaRepository<AllocationRequestEntity, String> {

    Page<AllocationRequestEntity> findByProjectId(String projectId, Pageable pageable);
}
