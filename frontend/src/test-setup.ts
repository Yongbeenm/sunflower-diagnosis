/**
 * Vitest global test setup.
 *
 * Imports @testing-library/jest-dom to augment Vitest's `expect` with
 * DOM-specific matchers like toBeInTheDocument(), toHaveValue(), etc.
 *
 * This file is referenced in vite.config.ts → test.setupFiles.
 */
import "@testing-library/jest-dom";
