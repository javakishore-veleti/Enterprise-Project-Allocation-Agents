package com.javakishore.epaa.employee.dao;

import com.javakishore.epaa.employee.entities.EmployeeEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EmployeeRepository extends JpaRepository<EmployeeEntity, String> {

    Page<EmployeeEntity> findByFullNameContainingIgnoreCaseOrTitleContainingIgnoreCase(
            String fullName, String title, Pageable pageable);
}
