package com.javakishore.epaa.project.services;

public class ProjectNotFoundException extends RuntimeException {
    public ProjectNotFoundException(String id) {
        super("Project not found: " + id);
    }
}
