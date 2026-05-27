package com.javakishore.epaa.project.entities;

import com.javakishore.epaa.project.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import java.time.LocalDate;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "projects")
@Getter
@Setter
public class ProjectEntity extends BaseEntity {

    @Column(name = "name", nullable = false, length = 200)
    private String name;

    @Column(name = "client_name", length = 160)
    private String clientName;

    @Column(name = "priority", length = 20)
    private String priority;

    @Column(name = "complexity", length = 20)
    private String complexity;

    @Column(name = "duration_weeks")
    private Integer durationWeeks;

    @Column(name = "required_headcount")
    private Integer requiredHeadcount;

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "status", length = 30)
    private String status;
}
