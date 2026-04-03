package com.edu.user.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.Map;

@FeignClient(name = "edu-user-service", fallback = UserFeignClientFallback.class)
public interface UserFeignClient {
    
    @GetMapping("/user/{id}")
    Map<String, Object> getUserById(@PathVariable("id") Long id);
}
