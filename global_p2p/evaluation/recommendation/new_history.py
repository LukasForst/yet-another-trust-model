from global_p2p.model.peer_trust_data import PeerTrustData
from global_p2p.model.recommendation_history import RecommendationHistoryRecord, RecommendationHistory
from global_p2p.model.recommendation_response import Recommendation
from global_p2p.model.trust_model_configuration import TrustModelConfiguration
from global_p2p.utils.time import now


def create_recommendation_history_for_peer(
        configuration: TrustModelConfiguration,
        peer: PeerTrustData,
        recommendation: Recommendation,
        history_factor: float,
        er_ij: float,
        ecb_ij: float,
        eib_ij: float
) -> RecommendationHistory:
    """
    Creates new recommendation_history for given peer and its recommendations.

    :param configuration: configuration for current trust model
    :param peer: peer "k" which provided recommendation r
    :param recommendation: recommendation provided by peer k
    :param history_factor: int(mean(size of history) / maximal history size)
    :param er_ij: estimation about reputation
    :param ecb_ij: estimation about competence belief
    :param eib_ij: estimation about integrity belief
    :return:
    """
    rs_ik = __compute_recommendation_satisfaction_parameter(recommendation, er_ij, ecb_ij, eib_ij)
    rw_ik = __compute_weight_of_recommendation(configuration, recommendation, history_factor)

    updated_history = peer.recommendation_history + [RecommendationHistoryRecord(satisfaction=rs_ik,
                                                                                 weight=rw_ik,
                                                                                 timestamp=now())]
    # fix history len if we reached max size
    if len(updated_history) > configuration.recommendation_history_max_size:
        last_idx = len(updated_history)
        updated_history = updated_history[last_idx - configuration.recommendation_history_max_size: last_idx]

    return updated_history


def __compute_recommendation_satisfaction_parameter(
        recommendation: Recommendation,
        er_ij: float,
        ecb_ij: float,
        eib_ij: float
) -> float:
    """
    Computes satisfaction parameter - how much was peer satisfied with provided data.

    :param recommendation: recommendation from the peer
    :param er_ij: estimation about reputation
    :param ecb_ij: estimation about competence belief
    :param eib_ij: estimation about integrity belief
    :return: recommendation satisfaction rs_ik
    """
    r_diff = 1 - abs(recommendation.recommendation - er_ij) / er_ij
    cb_diff = 1 - abs(recommendation.competence_belief - ecb_ij) / ecb_ij
    ib_diff = 1 - abs(recommendation.integrity_belief - eib_ij) / eib_ij
    return (r_diff + cb_diff + ib_diff) / 3


def __compute_weight_of_recommendation(
        configuration: TrustModelConfiguration,
        recommendation: Recommendation,
        history_factor: float
) -> float:
    """
    Computes weight of recommendation - in model's notation rw^z_ik.
    :param configuration: current trust model config
    :param recommendation: recommendation from the peer
    :param history_factor: int(mean(size of history) / maximal history size)
    :return: recommendation weight rw^z_ik
    """
    service_history = recommendation.service_history_size / configuration.service_history_max_size
    used_peers = recommendation.initial_reputation_provided_by_count / configuration.recommending_peers_max_count
    return history_factor * service_history + (1 - history_factor) * used_peers
