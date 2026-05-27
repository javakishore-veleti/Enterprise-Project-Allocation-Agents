package com.javakishore.epaa.project.entities;

import com.javakishore.epaa.project.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/** Free-text brief for a project (1:1). The parsed/embedded fields are owned by
 * the agents/Datalake layer, not this CRUD service. */
@Entity
@Table(name = "project_briefs")
@Getter
@Setter
public class ProjectBriefEntity extends BaseEntity {

    @Column(name = "project_id", nullable = false, length = 36)
    private String projectId;

    @Column(name = "brief_text", columnDefinition = "text")
    private String briefText;
}
