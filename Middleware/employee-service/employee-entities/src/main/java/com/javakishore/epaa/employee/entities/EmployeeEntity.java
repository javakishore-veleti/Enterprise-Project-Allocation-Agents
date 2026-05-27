package com.javakishore.epaa.employee.entities;

import com.javakishore.epaa.employee.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/** Employee record (CRUD-owned by employee-service). UUID-string PK via BaseEntity. */
@Entity
@Table(name = "employees")
@Getter
@Setter
public class EmployeeEntity extends BaseEntity {

    @Column(name = "full_name", nullable = false, length = 160)
    private String fullName;

    @Column(name = "title", length = 120)
    private String title;

    @Column(name = "seniority", length = 40)
    private String seniority;

    @Column(name = "years_experience")
    private Integer yearsExperience;

    @Column(name = "performance_score")
    private Double performanceScore;

    @Column(name = "availability_state", length = 40)
    private String availabilityState;

    @Column(name = "capacity_hours_per_week")
    private Integer capacityHoursPerWeek;

    @Column(name = "profile_text", columnDefinition = "text")
    private String profileText;
}
