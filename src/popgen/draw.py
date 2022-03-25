import numpy as np
import pandas as pd
from scipy import stats


class Draw_Population(object):
    def __init__(
        self,
        scenario_config,
        geo_ids,
        geo_row_idx,
        geo_frequencies,
        geo_constraints,
        geo_stacked,
        region_sample_weights,
    ):
        self.scenario_config = scenario_config
        self.geo_ids = geo_ids
        self.geo_row_idx = geo_row_idx
        self.geo_frequencies = geo_frequencies
        self.geo_constraints = geo_constraints
        self.geo_stacked = geo_stacked
        self.region_sample_weights = region_sample_weights

        self.iterations = self.scenario_config.parameters.draws.iterations
        self.seed = self.scenario_config.parameters.draws.seed
        self.pvalue_tolerance = self.scenario_config.parameters.draws.pvalue_tolerance
        self.geo_id_rows_syn_dict = {}
        self.performance_columns = ["p_value", "iterations", "chi_sq_stat"]
        self.draws_performance = pd.DataFrame(
            index=self.geo_ids, columns=self.performance_columns)

    def draw_population(self):
        np.random.seed(self.seed)
        for geo_id in self.geo_ids:
            #  "For geo:", geo_id
            geo_sample_weights = self.region_sample_weights.loc[:, geo_id]
            geo_cumulative_weights = self._return_cumulative_probability(
                geo_sample_weights)
            geo_id_frequencies = self.geo_frequencies.loc[geo_id, :]
            geo_id_constraints = self.geo_constraints.loc[geo_id, :]

            if geo_id_frequencies.sum() == 0:
                continue

            p_value_max = -1
            for iter in range(self.iterations):
                #  "Iter is:", iter, self.iterations
                seed = self.seed + iter
                geo_id_rows_syn = self._pick_households(
                    geo_id_frequencies, geo_cumulative_weights)
                stat, p_value = self._measure_match(
                    geo_id_rows_syn, geo_id_constraints)
                if p_value > self.pvalue_tolerance:
                    (p_value_max, geo_id_rows_syn_max, iter_max, stat_max, max_found) = (
                        p_value,
                        geo_id_rows_syn,
                        iter,
                        stat,
                        True,
                    )
                    self.draws_performance.loc[geo_id, self.performance_columns] = (
                        p_value_max, iter, stat_max)
                    break
                elif p_value > p_value_max:
                    (p_value_max, geo_id_rows_syn_max, iter_max, stat_max, max_found) = (
                        p_value,
                        geo_id_rows_syn,
                        iter,
                        stat,
                        False,
                    )
                    self.draws_performance.loc[geo_id, self.performance_columns] = (
                        p_value_max, iter, stat_max)

            #  "Max found:", max_found, geo_id_frequencies.sum()
            #  "Max iter: %d, %f, %f" % (iter_max, p_value_max, stat_max)
            # self.syn_population.add_records_for_geo_id(
            #    geo_id, geo_id_rows_syn_max)
            self.geo_id_rows_syn_dict[geo_id] = geo_id_rows_syn_max
        #  self.draws_performance

    def _return_cumulative_probability(self, geo_sample_weights):
        geo_cumulative_weights = {}

        for column in self.geo_frequencies.columns.values:
            rows = self.geo_row_idx[column]
            weights = geo_sample_weights.take(rows)
            geo_cumulative_weights[column] = (weights / weights.sum()).cumsum()

            #  geo_cumulative_weights[column]
        return geo_cumulative_weights

    def _pick_households(self, geo_id_frequencies, geo_cumulative_weights):
        last = 0
        (geo_id_frequencies.sum())
        rand_numbers = np.random.random(int(geo_id_frequencies.sum()))
        list_rows_syn_subpop = []
        for column in self.geo_frequencies.columns.values:
            rows = self.geo_row_idx[column]
            column_frequency = geo_id_frequencies[column]
            # (last, int(column_frequency))
            column_bins = np.searchsorted(
                geo_cumulative_weights[column], (rand_numbers[int(
                    last): int(last) + int(column_frequency)]), side="right"
            )
            last += column_frequency
            list_rows_syn_subpop.append(rows.take(column_bins))
        geo_id_rows_syn = np.sort(np.concatenate(list_rows_syn_subpop))
        return geo_id_rows_syn

    def _measure_match(self, geo_id_rows_syn, geo_id_constraints, over_columns=None):

        geo_id_constraints.name = "constraint"
        geo_id_synthetic = self.geo_stacked.take(geo_id_rows_syn).sum()
        # (geo_id_synthetic)
        geo_id_synthetic = pd.DataFrame(
            geo_id_synthetic, columns=["synthetic_count"])
        geo_id_synthetic = geo_id_synthetic.join(
            geo_id_constraints, how="inner")
        (geo_id_synthetic["synthetic_count"],
              geo_id_synthetic["constraint"])
        stat, p_value = stats.chisquare(
            geo_id_synthetic["synthetic_count"], geo_id_synthetic["constraint"])
        return stat, p_value
