import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(js.configs.recommended, ...tseslint.configs.recommended, {
  files: ['src/**/*.{ts,tsx}'],
  languageOptions: { globals: { document: 'readonly', window: 'readonly', fetch: 'readonly', URL: 'readonly', Blob: 'readonly', console: 'readonly', setTimeout: 'readonly', setInterval: 'readonly', clearInterval: 'readonly' } },
});
