package com.javakishore.epaa.notification.dao;

import com.javakishore.epaa.notification.entities.NotificationEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NotificationRepository extends JpaRepository<NotificationEntity, String> {

    Page<NotificationEntity> findByStatus(String status, Pageable pageable);

    Page<NotificationEntity> findByEmployeeId(String employeeId, Pageable pageable);
}
