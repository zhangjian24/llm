package com.edu.user.config;

import com.alibaba.nacos.api.naming.NamingService;
import com.alibaba.nacos.spring.context.annotation.EnableNacos;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableNacos(globalProperties = @com.alibaba.nacos.spring.context.annotation.NacosProperties(serverAddr = "${spring.cloud.nacos.discovery.server-addr:127.0.0.1:8848}"))
public class NacosConfig {
}
