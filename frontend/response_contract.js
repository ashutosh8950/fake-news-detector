(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.TruthScanResponseContract = factory();
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function isObject(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function isBoundedNumber(value) {
    return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 100;
  }

  function isNonNegativeInteger(value) {
    return Number.isInteger(value) && value >= 0;
  }

  function validEnsemble(data) {
    if (!isObject(data)) return false;
    if (typeof data.ensemble_is_fake !== 'boolean') return false;
    if (!['FAKE NEWS', 'REAL NEWS'].includes(data.ensemble_label)) return false;
    if (!isBoundedNumber(data.overall_confidence)) return false;
    if (!isNonNegativeInteger(data.fake_votes) || !isNonNegativeInteger(data.real_votes)) return false;
    if (!Number.isInteger(data.total_models) || data.total_models < 1) return false;
    if (data.fake_votes + data.real_votes !== data.total_models) return false;
    if (!isObject(data.models) || Object.keys(data.models).length !== data.total_models) return false;

    return Object.values(data.models).every((model) => (
      isObject(model) &&
      typeof model.name === 'string' && model.name.trim().length > 0 &&
      typeof model.label === 'string' && ['Fake', 'Real'].includes(model.label) &&
      typeof model.is_fake === 'boolean' &&
      isBoundedNumber(model.confidence) &&
      model.is_fake === (model.label === 'Fake')
    ));
  }

  function validDeep(data) {
    if (!isObject(data)) return false;
    if (typeof data.label !== 'string' || !['FAKE', 'REAL'].includes(data.label.trim().toUpperCase())) return false;
    if (!isBoundedNumber(data.confidence)) return false;
    return data.processing_time_ms === undefined || (
      typeof data.processing_time_ms === 'number' &&
      Number.isFinite(data.processing_time_ms) &&
      data.processing_time_ms >= 0
    );
  }

  function validate(mode, data) {
    return mode === 'deep' ? validDeep(data) : validEnsemble(data);
  }

  return { validate };
}));
