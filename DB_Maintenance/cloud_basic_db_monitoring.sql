-- Check partition usage
SELECT 
  TABLE_NAME,
  PARTITION_NAME,
  TABLE_ROWS,
  AVG_ROW_LENGTH,
  DATA_LENGTH / 1024 / 1024 as DATA_MB
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_SCHEMA = 'LiteratureScrapeDB'
  AND PARTITION_NAME IS NOT NULL
ORDER BY TABLE_NAME, PARTITION_ORDINAL_POSITION;

-- Index usage statistics
SELECT 
  TABLE_NAME,
  INDEX_NAME,
  CARDINALITY,
  INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'LiteratureScrapeDB'
ORDER BY TABLE_NAME, INDEX_NAME;


-- Slow queries analysis
-- Enable slow query log and analyze with pt-query-digest (See Cloud/BQ config or my.cnf)
-- ---------
-- There might be better options for alterting that are more Kafka/RabbitMQ - like than raw SQL... But they suffice. 
-- since monitoring/observability is just easier directly with GCP services
-- ---------
-- Query performance monitoring table
CREATE TABLE query_performance_log (
  log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  query_type VARCHAR(100),
  query_text TEXT,
  execution_time_ms BIGINT,
  rows_examined BIGINT,
  rows_returned BIGINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_query_type (query_type),
  INDEX idx_execution_time (execution_time_ms DESC)
) ENGINE=InnoDB;

-- Trigger to log slow queries (>2 seconds)
DELIMITER //
CREATE TRIGGER log_slow_query
AFTER INSERT ON query_performance_log
FOR EACH ROW
BEGIN
  IF NEW.execution_time_ms > 2000 THEN
    INSERT INTO alert_queue (alert_type, message, severity, created_at)
    VALUES (
      'slow_query',
      CONCAT('Slow query detected: ', SUBSTRING(NEW.query_text, 1, 200)),
      'warning',
      NOW()
    );
  END IF;
END //
DELIMITER ;

-- Alert queue for monitoring system
CREATE TABLE alert_queue (
  alert_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  alert_type VARCHAR(50),
  message TEXT,
  severity ENUM('info', 'warning', 'critical'),
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved_at TIMESTAMP NULL,
  
  INDEX idx_severity_unresolved (severity, resolved, created_at)
) ENGINE=InnoDB;