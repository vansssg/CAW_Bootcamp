# Module 03 FIX — how Jamie’s doc should change

## Immediate edits required before approval
1. **Add Alternatives:** e.g. managed queue (SQS), DB outbox + worker, cloud Pub/Sub — each with ops cost / ordering / latency tradeoffs.  
2. **Move DB capacity to Open Questions** until a named load test on *event-shaped* writes is attached; delete “plenty of headroom” as fact.  
3. **Rewrite mitigations:**  
   - Lag: alert if lag > N messages for M minutes; auto-scale consumers to max K; page `#oncall-analytics`.  
   - Kafka unavailable: define producer policy (fail API publish path vs local buffer with max size + metric); never “RF3” alone.  
4. **Add Open Questions:** ownership of Kafka, multi-AZ cost, PII in events, exactly-once vs at-least-once for purchases.

## Prevention checklist (reuse on our rate-limit RFC)
- [x] Alternatives present with real pros  
- [x] Do-nothing risk  
- [x] Open questions  
- [x] Mitigations with measurable triggers (latency rollback)
