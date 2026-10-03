from codeable_models import CClass, add_links, CBundle, CStereotype
from src.metamodels.guidance_metamodel import (
    practice,
    decision,
    add_decision_option_link,
    positive,
    negative,
    force,
    mandatory_next,
    feeds_into_via_trigger, complements_but_limited_by, tense_interaction_requires_separation,
    enables_next_decision, can_be_combined_with_next_decision, constrains, complements
)

def add_force_relations(force_relations_definition):
    for pr in force_relations_definition.keys():
        for fc in force_relations_definition[pr]:
            stereotype = (force_relations_definition[pr])[fc]
            add_links(
                {pr: fc},
                role_name="forces",
                stereotype_instances=stereotype,
            )


def get_connected_elements(element, forces=False):
    def helper(el, visited, depth=0):
        key = el.class_object
        if key in visited:
            return []
        visited.add(key)
        result = [key]
        if depth < 1 or forces:
            for le in el.linked:
                result.extend(helper(le, visited, depth + 1))
        return result
    return helper(element, set())


# --------------------------------------------------------------------
# Decision Drivers (Forces)
# --------------------------------------------------------------------
safety_constraints_force = CClass(force, "SafetyConstraints")
environment_non_stationarity_force = CClass(
    force, "EnvironmentNonStationarity"
)
catastrophic_degradation_force = CClass(force, "CatastrophicDegradation")
delayed_sparse_rewards_force = CClass(force, "DelayedSparseRewards")

environment_non_stationarity_force = environment_non_stationarity_force
delayed_sparse_rewards_force = delayed_sparse_rewards_force
catastrophic_degradation_force = catastrophic_degradation_force
monitoring_independence_force = CClass(force, "MonitoringIndependence")
signal_non_stationarity_force = CClass(force, "SignalNonStationarity")
goodharts_law_force = CClass(force, "GoodhartsLaw")
covariate_shift_force = CClass(force, "CovariateShift")
evaluation_mismatch_force = CClass(force, "EvaluationMismatch")
reward_model_staleness_force = CClass(force, "RewardModelStaleness")
alignment_impermanence_force = CClass(force, "AlignmentImpermanence")
scale_compounding_force = CClass(force, "ScaleCompounding")
hidden_variable_shift_force = CClass(force, "HiddenVariableShift")
drift_inevitability_force = CClass(force, "DriftInevitability")
monitoring_multiplicity_force = CClass(force, "MonitoringMultiplicity")
slo_breach_detection_force = CClass(force, "SLOBreachDetection")
security_compliance_force = CClass(force, "SecurityCompliance")
governance_traceability_force = CClass(force, "GovernanceTraceability")

recovery_speed_force = CClass(force, "RecoverySpeed")
emergent_instability_force = CClass(force, "EmergentInstability")
stateful_rollback_complexity_force = CClass(
    force, "StatefulRollbackComplexity"
)
flapping_risk_force = CClass(force, "FlappingRisk")
audit_requirement_force = CClass(force, "AuditRequirement")
retraining_cost_force = CClass(force, "RetrainingCost")
catastrophic_forgetting_force = CClass(force, "CatastrophicForgetting")
latency_slo_pressure_force = CClass(force, "LatencySLOPressure")

detection_latency_force = CClass(force, "DetectionLatency")
signal_non_stationarity_force = signal_non_stationarity_force
episodic_structure_force = CClass(force, "EpisodicStructure")
reference_dataset_availability_force = CClass(
    force, "ReferenceDatasetAvailability"
)
monitoring_independence_force = monitoring_independence_force
goodharts_law_force = goodharts_law_force
drift_inevitability_force = drift_inevitability_force
reward_inflation_risk_force = CClass(force, "RewardInflationRisk")
governance_traceability_force = governance_traceability_force

false_alarm_cost_force = CClass(force, "FalseAlarmCost")
signal_non_stationarity_force = signal_non_stationarity_force
episodic_structure_force = episodic_structure_force
flapping_risk_force = flapping_risk_force
governance_traceability_force = governance_traceability_force

goodharts_law_force = goodharts_law_force
specification_gaming_force = CClass(force, "SpecificationGaming")
scale_compounding_force = scale_compounding_force
evaluator_deception_force = CClass(force, "EvaluatorDeception")
covert_misalignment_force = CClass(force, "CovertMisalignment")
unhackability_hardness_force = CClass(force, "UnhackabilityHardness")
alignment_side_effects_force = CClass(force, "AlignmentSideEffects")
in_context_reward_hacking_force = CClass(force, "InContextRewardHacking")
evaluator_hackability_force = CClass(force, "EvaluatorHackability")
hacking_generalisation_force = CClass(force, "HackingGeneralisation")
monitoring_evasion_force = CClass(force, "MonitoringEvasion")
context_dependent_misalignment_force = CClass(
    force, "ContextDependentMisalignment"
)
verifier_exploitability_force = CClass(force, "VerifierExploitability")
reward_model_staleness_force = reward_model_staleness_force
in_context_reward_hacking_deploy_force = in_context_reward_hacking_force
cot_faithfulness_force = CClass(force, "CoTFaithfulness")


# --------------------------------------------------------------------
# Decision Options
# --------------------------------------------------------------------
# ADD 1: Safe Exploration Strategy Selection
conservative_policy_updates_option = CClass(
    practice, "Conservative Policy Updates"
)
constrained_policy_optimisation_option = CClass(
    practice, "Constrained Policy Optimisation"
)
multi_armed_bandit_integration_option = CClass(
    practice, "Multi-Armed Bandit Integration"
)

# ADD 2: Production Monitoring Signal Selection
rl_specific_metric_tracking_option = CClass(
    practice, "RL-Specific Metric Tracking"
)
business_outcome_correlation_option = CClass(
    practice, "Business Outcome Correlation"
)
ab_policy_comparison_option = CClass(practice, "A/B Policy Comparison")
covariance_weighted_reward_signal_option = CClass(
    practice, "Covariance-Weighted Reward Signal"
)
feature_distribution_drift_option = CClass(
    practice, "Feature Distribution Drift (KL/MMD)"
)
reward_proxy_gap_tracking_option = CClass(
    practice, "Reward Proxy Gap Tracking"
)
embedding_drift_detection_option = CClass(
    practice, "Embedding Drift Detection"
)
activation_delta_monitoring_option = CClass(
    practice, "Activation Delta Monitoring"
)
reward_model_score_monitoring_option = CClass(
    practice, "Reward Model Score Monitoring"
)
kl_divergence_from_reference_policy_option = CClass(
    practice, "KL Divergence from Reference Policy"
)
metric_divergence_monitoring_option = CClass(
    practice, "Metric Divergence Monitoring"
)
shield_intervention_rate_tracking_option = CClass(
    practice, "Shield Intervention Rate Tracking"
)
context_sliced_signal_monitoring_option = CClass(
    practice, "Context-Sliced Signal Monitoring"
)
action_failure_rate_monitoring_option = CClass(
    practice, "Action Failure Rate Monitoring"
)
latency_slo_monitoring_option = CClass(
    practice, "Latency SLO Monitoring"
)
security_significant_signals_option = CClass(
    practice, "Security-Significant Signals"
)

# ADD 3: Automated Response Mechanism Selection
automated_circuit_breakers_option = CClass(
    practice, "Automated Circuit Breakers"
)
policy_rollback_option = CClass(practice, "Policy Rollback")
rollback_lr_stabilisation_option = CClass(
    practice, "Rollback with Learning-Rate Stabilisation"
)
blue_green_traffic_shift_option = CClass(
    practice, "Blue-Green Traffic Shift"
)
graceful_degradation_option = CClass(practice, "Graceful Degradation")
hitl_intervention_option = CClass(
    practice, "Human-in-the-Loop Intervention"
)
continuous_adaptation_option = CClass(
    practice, "Continuous Adaptation (Fine-tuning)"
)
mid_run_reward_function_update_option = CClass(
    practice, "Mid-Run Reward Function Update"
)
shadow_deployment_option = CClass(practice, "Shadow Deployment")

# ADD 4: Reward Degradation Test Statistic Selection
covariance_weighted_mean_test_option = CClass(
    practice, "Covariance-Weighted Mean Test"
)
naive_simple_mean_option = CClass(practice, "Naive Simple Mean")
cusum_sequential_test_option = CClass(
    practice, "CUSUM Sequential Test"
)
hotelling_multivariate_test_option = CClass(
    practice, "Hotelling Multivariate Test"
)
embedding_based_drift_detection_option = CClass(
    practice, "Embedding-Based Drift Detection"
)
psi_kl_input_distribution_test_option = CClass(
    practice, "PSI / KL Input Distribution Test"
)

# ADD 5: False Alarm Rate Control Method
bfar_option = CClass(practice, "Bootstrap FAR (BFAR)")
fixed_statistical_threshold_option = CClass(
    practice, "Fixed Statistical Threshold"
)
adaptive_threshold_option = CClass(practice, "Adaptive Threshold")
variance_tuned_threshold_option = CClass(
    practice, "Variance-Tuned Threshold"
)

# ADD 6: Reward Hacking Detection Strategy
metric_divergence_detection_option = CClass(
    practice, "Metric Divergence Detection"
)
cot_analysis_option = CClass(
    practice, "Chain-of-Thought (CoT) Analysis"
)
adversarial_testing_option = CClass(practice, "Adversarial Testing")
ensemble_reward_model_agreement_option = CClass(
    practice, "Ensemble Reward Model Agreement"
)
behavioural_testing_heldout_envs_option = CClass(
    practice, "Behavioural Testing on Held-Out Environments"
)
anomaly_detection_trusted_policy_option = CClass(
    practice, "Anomaly Detection with Trusted Policy"
)
deployment_time_feedback_loop_simulation_option = CClass(
    practice, "Deployment-Time Feedback Loop Simulation"
)
reward_model_vs_outcome_divergence_option = CClass(
    practice, "Reward Model vs Outcome Divergence"
)
vft_self_report_option = CClass(
    practice, "Verbalisation / Self-Report (VFT)"
)

# ADD 7: Reward Hacking Mitigation Architecture
regularisation_to_reference_policy_option = CClass(
    practice, "Regularisation to Reference Policy"
)
reward_function_redesign_option = CClass(
    practice, "Reward Function Redesign"
)
preference_as_reward_option = CClass(
    practice, "Preference as Reward (PAR)"
)
inoculation_prompting_option = CClass(
    practice, "Inoculation Prompting"
)
targeted_rlhf_option = CClass(practice, "Targeted RLHF")
periodic_reward_model_refresh_option = CClass(
    practice, "Periodic Reward-Model Refresh"
)
sft_non_gaming_data_option = CClass(
    practice, "SFT on Non-Gaming Data"
)
gated_reward_accumulation_option = CClass(
    practice, "Gated Reward Accumulation (G-RA)"
)
myopic_optimisation_option = CClass(
    practice, "Myopic Optimisation (MONA-like)"
)
decoupled_approval_feedback_option = CClass(
    practice, "Decoupled Approval / Feedback"
)


# --------------------------------------------------------------------
# Force Relations (positive / negative)
# --------------------------------------------------------------------
add_force_relations(
    {
        constrained_policy_optimisation_option: {
            safety_constraints_force: positive,
        },
        conservative_policy_updates_option: {
            safety_constraints_force: positive,
            environment_non_stationarity_force: positive,
            catastrophic_degradation_force: positive,
        },
        multi_armed_bandit_integration_option: {
            delayed_sparse_rewards_force: positive,
        },
    }
)

add_force_relations(
    {
        rl_specific_metric_tracking_option: {
            environment_non_stationarity_force: positive,
            delayed_sparse_rewards_force: positive,
            catastrophic_degradation_force: positive,
            signal_non_stationarity_force: positive,
            monitoring_independence_force: positive,
        },
        business_outcome_correlation_option: {
            delayed_sparse_rewards_force: positive,
            evaluation_mismatch_force: positive,
            goodharts_law_force: positive,
        },
        ab_policy_comparison_option: {
            catastrophic_degradation_force: positive,
            environment_non_stationarity_force: positive,
        },
        covariance_weighted_reward_signal_option: {
            signal_non_stationarity_force: positive,
            drift_inevitability_force: positive,
        },
        feature_distribution_drift_option: {
            covariate_shift_force: positive,
            drift_inevitability_force: positive,
        },
        reward_proxy_gap_tracking_option: {
            evaluation_mismatch_force: positive,
            goodharts_law_force: positive,
        },
        embedding_drift_detection_option: {
            covariate_shift_force: positive,
            hidden_variable_shift_force: positive,
            drift_inevitability_force: positive,
        },
        activation_delta_monitoring_option: {
            hidden_variable_shift_force: positive,
            alignment_impermanence_force: positive,
        },
        reward_model_score_monitoring_option: {
            reward_model_staleness_force: positive,
            alignment_impermanence_force: positive,
        },
        kl_divergence_from_reference_policy_option: {
            reward_model_staleness_force: positive,
            goodharts_law_force: positive,
        },
        metric_divergence_monitoring_option: {
            goodharts_law_force: positive,
            scale_compounding_force: positive,
        },
        shield_intervention_rate_tracking_option: {
            hidden_variable_shift_force: positive,
            security_compliance_force: positive,
        },
        context_sliced_signal_monitoring_option: {
            monitoring_multiplicity_force: positive,
            drift_inevitability_force: positive,
        },
        action_failure_rate_monitoring_option: {
            slo_breach_detection_force: positive,
            catastrophic_degradation_force: positive,
        },
        latency_slo_monitoring_option: {
            slo_breach_detection_force: positive,
            latency_slo_pressure_force: positive,
        },
        security_significant_signals_option: {
            security_compliance_force: positive,
            monitoring_evasion_force: positive,
        },
    }
)

add_force_relations(
    {
        automated_circuit_breakers_option: {
            catastrophic_degradation_force: positive,
            safety_constraints_force: positive,
            security_compliance_force: positive,
        },

        rollback_lr_stabilisation_option: {
            emergent_instability_force: positive,
            catastrophic_forgetting_force: positive,
        },
        blue_green_traffic_shift_option: {
            stateful_rollback_complexity_force: positive,
            latency_slo_pressure_force: positive,
        },
        graceful_degradation_option: {
            environment_non_stationarity_force: positive,
            retraining_cost_force: positive,
            latency_slo_pressure_force: positive,
        },
        hitl_intervention_option: {
            safety_constraints_force: positive,
            audit_requirement_force: positive,
        },
        continuous_adaptation_option: {
            environment_non_stationarity_force: positive,
            retraining_cost_force: positive,
            catastrophic_forgetting_force: negative,
        },
        mid_run_reward_function_update_option: {
            reward_inflation_risk_force: positive,
            evaluation_mismatch_force: positive,
        },
        shadow_deployment_option: {
            emergent_instability_force: positive,
            audit_requirement_force: positive,
        },
        policy_rollback_option: {
            stateful_rollback_complexity_force: negative,
            catastrophic_degradation_force: positive,
            emergent_instability_force: positive,
            audit_requirement_force: positive,
        },
})

add_force_relations({
    automated_circuit_breakers_option: {flapping_risk_force: negative},
    policy_rollback_option: {flapping_risk_force: negative},
    rollback_lr_stabilisation_option: {flapping_risk_force: negative},
    blue_green_traffic_shift_option: {flapping_risk_force: negative},
    graceful_degradation_option: {flapping_risk_force: negative},
    hitl_intervention_option: {flapping_risk_force: negative},
    continuous_adaptation_option: {flapping_risk_force: negative},
    mid_run_reward_function_update_option: {flapping_risk_force: negative},
    shadow_deployment_option: {flapping_risk_force: negative},
})

add_force_relations({
    policy_rollback_option: {recovery_speed_force: positive},
    continuous_adaptation_option: {recovery_speed_force: negative},
})

add_force_relations(
    {
        covariance_weighted_mean_test_option: {
            detection_latency_force: positive,
        },
        naive_simple_mean_option: {
            governance_traceability_force: positive,
            reference_dataset_availability_force: positive,
        },
        cusum_sequential_test_option: {
            detection_latency_force: positive,
            monitoring_independence_force: positive,
        },
        hotelling_multivariate_test_option: {
            detection_latency_force: positive,
            reference_dataset_availability_force: positive,
        },
        embedding_based_drift_detection_option: {
            drift_inevitability_force: positive,
            covariate_shift_force: positive,
        },
        psi_kl_input_distribution_test_option: {
            drift_inevitability_force: positive,
            covariate_shift_force: positive,
        },
    }
)

add_force_relations({
    covariance_weighted_mean_test_option: {
        signal_non_stationarity_force: positive,
    },
    naive_simple_mean_option: {
        signal_non_stationarity_force: negative,
    },
})

add_force_relations({
    covariance_weighted_mean_test_option: {
        episodic_structure_force: positive,
    },
    cusum_sequential_test_option: {
        episodic_structure_force: negative,
    },
})

add_force_relations(
    {
        bfar_option: {
            false_alarm_cost_force: positive,
            episodic_structure_force: positive,
            flapping_risk_force: positive,  # +BFAR
        },
        fixed_statistical_threshold_option: {
            governance_traceability_force: positive,
            false_alarm_cost_force: positive,
        },
        adaptive_threshold_option: {
            signal_non_stationarity_force: positive,
            flapping_risk_force: positive,
        },
        variance_tuned_threshold_option: {
            false_alarm_cost_force: positive,
            flapping_risk_force: positive,
        },
    }
)

add_force_relations({
    bfar_option: {
        signal_non_stationarity_force: positive,
    },
    fixed_statistical_threshold_option: {
        signal_non_stationarity_force: negative,
    },
})

add_force_relations({
    fixed_statistical_threshold_option: {
        flapping_risk_force: negative,
    },
})

add_force_relations(
    {
        metric_divergence_detection_option: {
            goodharts_law_force: positive,
            alignment_side_effects_force: positive,
        },
        cot_analysis_option: {
            evaluator_deception_force: positive,
            covert_misalignment_force: positive,
            cot_faithfulness_force: positive,
        },
        adversarial_testing_option: {
            specification_gaming_force: positive,
            hacking_generalisation_force: positive,
        },
        ensemble_reward_model_agreement_option: {
            unhackability_hardness_force: positive,
            evaluator_hackability_force: positive,
        },
        behavioural_testing_heldout_envs_option: {
            hacking_generalisation_force: positive,
            context_dependent_misalignment_force: positive,
        },
        anomaly_detection_trusted_policy_option: {
            alignment_side_effects_force: positive,
            monitoring_evasion_force: positive,
        },
        deployment_time_feedback_loop_simulation_option: {
            in_context_reward_hacking_force: positive,
            monitoring_evasion_force: positive,
        },
        reward_model_vs_outcome_divergence_option: {
            reward_model_staleness_force: positive,
            reward_inflation_risk_force: positive,
        },
        vft_self_report_option: {
            covert_misalignment_force: positive,
            context_dependent_misalignment_force: positive,
            verifier_exploitability_force: positive,
        },
    }
)

add_force_relations(
    {
        regularisation_to_reference_policy_option: {
            evaluator_deception_force: positive,
            evaluator_hackability_force: positive,
        },
        reward_function_redesign_option: {
            goodharts_law_force: positive,
            unhackability_hardness_force: positive,
        },
        preference_as_reward_option: {
            scale_compounding_force: positive,
            unhackability_hardness_force: positive,
        },
        inoculation_prompting_option: {
            covert_misalignment_force: positive,
            context_dependent_misalignment_force: positive,
        },
        targeted_rlhf_option: {
            scale_compounding_force: positive,
            alignment_impermanence_force: positive,
            context_dependent_misalignment_force: positive,
        },
        periodic_reward_model_refresh_option: {
            reward_model_staleness_force: positive,
            alignment_impermanence_force: positive,
        },
        sft_non_gaming_data_option: {
            evaluator_deception_force: positive,
            alignment_side_effects_force: positive,
        },
        gated_reward_accumulation_option: {
            unhackability_hardness_force: positive,
            reward_inflation_risk_force: positive,
        },
        myopic_optimisation_option: {
            unhackability_hardness_force: positive,
            scale_compounding_force: positive,
        },
        decoupled_approval_feedback_option: {
            evaluator_hackability_force: positive,
            evaluator_deception_force: positive,
        },
    }
)

# --------------------------------------------------------------------
# ADDs and Decision–Option Links
# --------------------------------------------------------------------
auto_retraining_option = continuous_adaptation_option
hybrid_verifiers_option = CClass(practice, "Hybrid Verifiers")
complex_scenario_testing_option = CClass(practice, "Complex Scenario Testing")
simple_chat_based_monitoring_option = CClass(practice, "Simple Chat-based Monitoring")

human_review_option = CClass(practice, "Human Review")
model_based_verifiers_option = CClass(practice, "Model-based Verifiers Alone")
rlhf_alone_option = CClass(practice, "RLHF Alone")

add_force_relations({
    rlhf_alone_option: {
        context_dependent_misalignment_force: negative,
    },
})

add_force_relations({
    complex_scenario_testing_option: {
        context_dependent_misalignment_force: positive,
    },
    simple_chat_based_monitoring_option: {
        context_dependent_misalignment_force: negative,
    },
})

add_force_relations({
    human_review_option: {
        evaluator_deception_force: negative,
    },
})

add_force_relations({
    hybrid_verifiers_option: {
        verifier_exploitability_force: positive,
    },
    model_based_verifiers_option: {
        verifier_exploitability_force: negative,
    },
})

# --------------------------------------------------------------------
# ADDs
# --------------------------------------------------------------------

# ADD 1
add1 = CClass(decision, "Safe Exploration Strategy Selection")
add_decision_option_link(add1, conservative_policy_updates_option, option_description="Limit policy changes per update")
add_decision_option_link(add1, constrained_policy_optimisation_option, option_description="Build safety constraints into optimisation")
add_decision_option_link(add1, multi_armed_bandit_integration_option, option_description="Use bandit approaches for low-risk exploration")

# ADD 2
add2 = CClass(decision, "Production Monitoring Signal Selection")
add_decision_option_link(add2, rl_specific_metric_tracking_option, option_description="Monitor episodic return, reward signals, entropy")
add_decision_option_link(add2, business_outcome_correlation_option, option_description="Track downstream KPIs and correlate with behaviour")
add_decision_option_link(add2, ab_policy_comparison_option, option_description="Continuously compare new policies against baselines")
add_decision_option_link(add2, covariance_weighted_reward_signal_option, option_description="Apply covariance-weighted tests to reward sequences")
add_decision_option_link(add2, feature_distribution_drift_option, option_description="Monitor covariate/input distribution shift")
add_decision_option_link(add2, reward_proxy_gap_tracking_option, option_description="Compare offline-validation with live proxy metrics")
add_decision_option_link(add2, embedding_drift_detection_option, option_description="Track drift in state/input embeddings or clusters")
add_decision_option_link(add2, activation_delta_monitoring_option, option_description="Monitor model-internal activation deltas")
add_decision_option_link(add2, reward_model_score_monitoring_option, option_description="Score production interactions with frozen reward model")
add_decision_option_link(add2, kl_divergence_from_reference_policy_option, option_description="Track divergence from known-good reference policy")
add_decision_option_link(add2, metric_divergence_monitoring_option, option_description="Compare optimised metric against related metrics")
add_decision_option_link(add2, shield_intervention_rate_tracking_option, option_description="Monitor safety shield override rate")
add_decision_option_link(add2, context_sliced_signal_monitoring_option, option_description="Compute metrics sliced by context/risk band")
add_decision_option_link(add2, latency_slo_monitoring_option, option_description="Monitor latency and error SLOs")
add_decision_option_link(add2, security_significant_signals_option, option_description="Monitor anomalous tool usage and data-access patterns")

# ADD 3
add3 = CClass(decision, "Automated Response Mechanism Selection")
add_decision_option_link(add3, automated_circuit_breakers_option, option_description="Switch to safe fallback when signals cross thresholds")
add_decision_option_link(add3, policy_rollback_option, option_description="Revert to previously validated baseline policy")
add_decision_option_link(add3, rollback_lr_stabilisation_option, option_description="Resume training with reduced learning rate after rollback")
add_decision_option_link(add3, blue_green_traffic_shift_option, option_description="Use infrastructure-level traffic switching")
add_decision_option_link(add3, graceful_degradation_option, option_description="Reduce agent autonomy while maintaining partial service")
add_decision_option_link(add3, hitl_intervention_option, option_description="Require human approval for high-risk decisions")
add_decision_option_link(add3, continuous_adaptation_option, option_description="Trigger finetuning on new data as response to drift")
add_decision_option_link(add3, mid_run_reward_function_update_option, option_description="Adjust reward functions mid-run")
add_decision_option_link(add3, shadow_deployment_option, option_description="Run candidate policies in observer mode")

# ADD 4
add4 = CClass(decision, "Reward Degradation Test Statistic Selection")
add_decision_option_link(add4, covariance_weighted_mean_test_option, option_description="Covariance-weighted means for correlated rewards")
add_decision_option_link(add4, naive_simple_mean_option, option_description="Compare recent mean reward to baseline")
add_decision_option_link(add4, cusum_sequential_test_option, option_description="Cumulative-sum change-detection on reward sequences")
add_decision_option_link(add4, hotelling_multivariate_test_option, option_description="Multivariate mean-shift tests over reward vectors")
add_decision_option_link(add4, embedding_based_drift_detection_option, option_description="Monitor state/observation embeddings for environment change")
add_decision_option_link(add4, psi_kl_input_distribution_test_option, option_description="PSI/KL divergence on inputs")

# ADD 5
add5 = CClass(decision, "False Alarm Rate Control Method")
add_decision_option_link(add5, bfar_option, option_description="Bootstrap methods to control false-alarm probability")
add_decision_option_link(add5, fixed_statistical_threshold_option, option_description="Static thresholds based on assumed distributions")
add_decision_option_link(add5, adaptive_threshold_option, option_description="Adjust thresholds online based on observed statistics")
add_decision_option_link(add5, variance_tuned_threshold_option, option_description="Calibrate thresholds to historical variance")

# ADD 6
add6 = CClass(decision, "Reward Hacking Detection Strategy")
add_decision_option_link(add6, metric_divergence_detection_option, option_description="Compare optimised metrics against related metrics")
add_decision_option_link(add6, cot_analysis_option, option_description="Inspect CoT traces for hacking intent")
add_decision_option_link(add6, adversarial_testing_option, option_description="Search for reward-hacking exploits")
add_decision_option_link(add6, ensemble_reward_model_agreement_option,
                         "Require agreement across multiple reward models")
add_decision_option_link(add6, behavioural_testing_heldout_envs_option, option_description="Test in unseen environments")
add_decision_option_link(add6, anomaly_detection_trusted_policy_option, option_description="Flag anomalous actions vs trusted baseline")
add_decision_option_link(add6, deployment_time_feedback_loop_simulation_option,
                         "Simulate self-refinement feedback loops")
add_decision_option_link(add6, reward_model_vs_outcome_divergence_option,
                         "Compare reward-model scores with actual outcomes")
add_decision_option_link(add6, vft_self_report_option, option_description="Train models to verbalise exploitation")
add_decision_option_link(add6, hybrid_verifiers_option, option_description="Combine multiple verification methods")
add_decision_option_link(add6, human_review_option, option_description="Periodic human review of sampled interactions")
add_decision_option_link(add6, model_based_verifiers_option, option_description="Model-based verifiers alone")
add_decision_option_link(add6, complex_scenario_testing_option, option_description="Test complex, high-risk scenarios")
add_decision_option_link(add6, simple_chat_based_monitoring_option, option_description="Simple chat-based checks")
add_decision_option_link(add6, rlhf_alone_option, option_description="RLHF alignment alone")

# ADD 7
add7 = CClass(decision, "Reward Hacking Mitigation Architecture")
add_decision_option_link(add7, regularisation_to_reference_policy_option, option_description="Penalise divergence from reference policy")
add_decision_option_link(add7, reward_function_redesign_option, option_description="Use multi-objective rewards and constraints")
add_decision_option_link(add7, preference_as_reward_option, option_description="Use latent preference representations as reward")
add_decision_option_link(add7, inoculation_prompting_option, option_description="Train with anti-hacking prompts")
add_decision_option_link(add7, targeted_rlhf_option, option_description="Focus RLHF on high-risk agentic evaluations")
add_decision_option_link(add7, periodic_reward_model_refresh_option, option_description="Retrain reward models on new preference data")
add_decision_option_link(add7, sft_non_gaming_data_option, option_description="SFT on data where hacking is detectable")
add_decision_option_link(add7, gated_reward_accumulation_option, option_description="Gate immediate rewards on long-term outcomes")
add_decision_option_link(add7, myopic_optimisation_option, option_description="Limit optimisation horizon")
add_decision_option_link(add7, decoupled_approval_feedback_option, option_description="Collect feedback independently of actions")

# ADD interdependencies
add_links({add2: add3},
          role_name="next decision", stereotype_instances=[feeds_into_via_trigger, mandatory_next, enables_next_decision],
          label="offer an abstraction layer for data access, monitoring enables automated response")

add_links({add2: add4},
          role_name="next decision", stereotype_instances=[constrains],
          label="signal repertoire determines available statistical tests")

add_links({add4: add5},
          role_name="next decision", stereotype_instances=[constrains],
          label="selected test determines applicable calibration methods")

add_links({add4: add6}, role_name="next decision", stereotype_instances=[complements_but_limited_by, can_be_combined_with_next_decision],
               label="downward drift detection needs gaming coverage, combine for full coverage")

add_links({add6: add4}, role_name="next decision", stereotype_instances=[complements])

add_links({add6: add7}, role_name="next decision", stereotype_instances=[tense_interaction_requires_separation],
               label="RLHF hiding degrades CoT")


# --------------------------------------------------------------------
# Views / Bundles
# --------------------------------------------------------------------
add_only_view = CBundle("add_only_view", elements=[add1, add2, add3, add4, add5, add6, add7])
add1_view = CBundle("add1_view", elements=get_connected_elements(add1))
add2_view = CBundle("add2_view", elements=get_connected_elements(add2))
add3_view = CBundle("add3_view", elements=get_connected_elements(add3))
add4_view = CBundle("add4_view", elements=get_connected_elements(add4))
add5_view = CBundle("add5_view", elements=get_connected_elements(add5))
add6_view = CBundle("add6_view", elements=get_connected_elements(add6))
add7_view = CBundle("add7_view", elements=get_connected_elements(add7))

all_elements = get_connected_elements(add1)
all_elements.extend(get_connected_elements(add2))
all_elements.extend(get_connected_elements(add3))
all_elements.extend(get_connected_elements(add4))
all_elements.extend(get_connected_elements(add5))
all_elements.extend(get_connected_elements(add6))
all_elements.extend(get_connected_elements(add7))

all_view = CBundle("all_view", elements=all_elements)

add1_view_with_forces = CBundle("add1_view_with_forces", elements=get_connected_elements(add1, True))
add2_view_with_forces = CBundle("add2_view_with_forces", elements=get_connected_elements(add2, True))
add3_view_with_forces = CBundle("add3_view_with_forces", elements=get_connected_elements(add3, True))
add4_view_with_forces = CBundle("add4_view_with_forces", elements=get_connected_elements(add4, True))
add5_view_with_forces = CBundle("add5_view_with_forces", elements=get_connected_elements(add5, True))
add6_view_with_forces = CBundle("add6_view_with_forces", elements=get_connected_elements(add6, True))
add7_view_with_forces = CBundle("add7_view_with_forces", elements=get_connected_elements(add7, True))

all_elements_with_forces = get_connected_elements(add1, True)
all_elements_with_forces.extend(get_connected_elements(add2, True))
all_elements_with_forces.extend(get_connected_elements(add3, True))
all_elements_with_forces.extend(get_connected_elements(add4, True))
all_elements_with_forces.extend(get_connected_elements(add5, True))
all_elements_with_forces.extend(get_connected_elements(add6, True))
all_elements_with_forces.extend(get_connected_elements(add7, True))

all_view_with_forces = CBundle("all_view_with_forces", elements=all_elements_with_forces)

rl_monitoring_adds_views = [
    add_only_view, {},
    add1_view, {},
    add2_view, {},
    add3_view, {},
    add4_view, {},
    add5_view, {},
    add6_view, {},
    add7_view, {},
    all_view, {},
    add1_view_with_forces, {},
    add2_view_with_forces, {},
    add3_view_with_forces, {},
    add4_view_with_forces, {},
    add5_view_with_forces, {},
    add6_view_with_forces, {},
    add7_view_with_forces, {},
    all_view_with_forces, {},
]
