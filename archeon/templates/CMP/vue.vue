<!-- @archeon:file -->
<!-- @glyph {GLYPH_QUALIFIED_NAME} -->
<!-- @intent {COMPONENT_INTENT} -->
<!-- @chain {CHAIN_REFERENCE} -->

<script setup>
// @archeon:section imports
// External dependencies and composables
{IMPORTS}
// @archeon:endsection

// @archeon:section props_and_state
// Reactive inputs and local UI state
defineProps({
{PROPS_DEFINITION}
});

{STATE_REFS}
// @archeon:endsection

// @archeon:section handlers
// Event handlers and computed properties
{HANDLERS}
// @archeon:endsection
</script>

<!-- @archeon:section render -->
<!-- Component template structure -->
<template>
  <div data-testid="{COMPONENT_NAME_KEBAB}">
{RENDER_CONTENT}
  </div>
</template>
<!-- @archeon:endsection -->

<!-- @archeon:section styles -->
<!-- Scoped component styles -->
<style scoped>
{STYLES}
</style>
<!-- @archeon:endsection -->
