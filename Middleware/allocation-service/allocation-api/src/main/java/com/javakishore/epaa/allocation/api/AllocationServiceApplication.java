package com.javakishore.epaa.allocation.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(scanBasePackages = "com.javakishore.epaa.allocation")
@EntityScan("com.javakishore.epaa.allocation.entities")
@EnableJpaRepositories("com.javakishore.epaa.allocation.dao")
public class AllocationServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(AllocationServiceApplication.class, args);
    }
}
