package com.javakishore.epaa.reporting.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(scanBasePackages = "com.javakishore.epaa.reporting")
@EntityScan("com.javakishore.epaa.reporting.entities")
@EnableJpaRepositories("com.javakishore.epaa.reporting.dao")
public class ReportingServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(ReportingServiceApplication.class, args);
    }
}
