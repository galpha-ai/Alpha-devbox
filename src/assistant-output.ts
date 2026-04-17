import { stripInternalTags } from './router.js';

export function stripStructuredResponseBlocks(content: string) {
  return content
    .replace(/<<<CHART_V1>>>[\s\S]*?<<<END_CHART_V1>>>/g, '')
    .replace(/<<<THESIS_REPORT_V1>>>[\s\S]*?<<<END_THESIS_REPORT_V1>>>/g, '');
}

export function prepareAssistantOutput(rawText: string) {
  const storedText = stripInternalTags(rawText).trim();
  const plainText = stripStructuredResponseBlocks(storedText).trim();

  return {
    storedText,
    plainText,
  };
}

export function formatAssistantDeliveryText(
  channelName: string,
  prepared: ReturnType<typeof prepareAssistantOutput>,
) {
  return channelName === 'web' ? prepared.storedText : prepared.plainText;
}
