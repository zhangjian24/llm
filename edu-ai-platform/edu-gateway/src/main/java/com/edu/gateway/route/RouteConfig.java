package com.edu.gateway.route;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RouteConfig {
    
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                .route("edu-user-service", r -> r
                        .path("/user/**")
                        .filters(f -> f
                                .stripPrefix(1)
                                .addRequestHeader("X-Gateway", "edu-gateway"))
                        .uri("lb://edu-user-service"))
                .route("edu-course-service", r -> r
                        .path("/course/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://edu-course-service"))
                .route("edu-homework-service", r -> r
                        .path("/homework/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://edu-homework-service"))
                .build();
    }
}
