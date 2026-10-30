/* Context continuity · schema validation.
   --------------------------------------------------------------------------
   The schemas in PROJECT-CONTEXT/schemas/ are plain JSON Schema (draft-07
   vocabulary). The platform takes no runtime dependencies, so this validates the
   subset the schemas actually use — type, enum, const, pattern, required,
   properties, additionalProperties, items, minItems, minLength, $ref (local) —
   and refuses any other keyword loudly rather than silently ignoring it, so a
   schema can never claim a rule this validator does not enforce. */
"use strict";

const KNOWN = new Set(["$schema", "$id", "$ref", "$comment", "title", "description", "type", "enum", "const",
  "pattern", "required", "properties", "additionalProperties", "items", "minItems", "minLength", "definitions", "default", "examples"]);

function typeOf(v) {
  if (v === null) return "null";
  if (Array.isArray(v)) return "array";
  if (Number.isInteger(v)) return "integer";
  return typeof v;
}
function typeMatches(want, v) {
  const t = typeOf(v);
  return want === t || (want === "number" && t === "integer");
}

function validate(schema, value, root, at, errors) {
  root = root || schema; at = at || "$"; errors = errors || [];
  for (const k of Object.keys(schema)) if (!KNOWN.has(k)) throw new Error("schema keyword not supported by the validator: " + k + " (at " + at + ")");
  if (schema.$ref) {
    const m = /^#\/definitions\/(.+)$/.exec(schema.$ref);
    if (!m || !root.definitions || !root.definitions[m[1]]) throw new Error("unresolvable $ref " + schema.$ref);
    return validate(root.definitions[m[1]], value, root, at, errors);
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some(t => typeMatches(t, value))) { errors.push(at + ": expected " + types.join("|") + ", got " + typeOf(value)); return errors; }
  }
  if (schema.const !== undefined && JSON.stringify(schema.const) !== JSON.stringify(value)) errors.push(at + ": must equal " + JSON.stringify(schema.const));
  if (schema.enum && !schema.enum.some(e => JSON.stringify(e) === JSON.stringify(value))) errors.push(at + ": " + JSON.stringify(value) + " not in " + JSON.stringify(schema.enum));
  if (typeof value === "string") {
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) errors.push(at + ": " + JSON.stringify(value) + " does not match /" + schema.pattern + "/");
    if (schema.minLength != null && value.length < schema.minLength) errors.push(at + ": shorter than " + schema.minLength);
  }
  if (Array.isArray(value)) {
    if (schema.minItems != null && value.length < schema.minItems) errors.push(at + ": fewer than " + schema.minItems + " items");
    if (schema.items) value.forEach((v, i) => validate(schema.items, v, root, at + "[" + i + "]", errors));
  }
  if (value && typeof value === "object" && !Array.isArray(value)) {
    for (const r of schema.required || []) if (value[r] === undefined) errors.push(at + ": missing required '" + r + "'");
    const props = schema.properties || {};
    for (const k of Object.keys(value)) {
      if (props[k]) validate(props[k], value[k], root, at + "." + k, errors);
      else if (schema.additionalProperties === false) errors.push(at + ": unexpected property '" + k + "'");
      else if (schema.additionalProperties && typeof schema.additionalProperties === "object") validate(schema.additionalProperties, value[k], root, at + "." + k, errors);
    }
  }
  return errors;
}

module.exports = { validate };
