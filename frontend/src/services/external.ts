import api from './api';
import type { ExternalTipResponse } from '../types';

export const externalService = {
  async getPrivacyTip(): Promise<ExternalTipResponse> {
    const response = await api.get('/external/privacy-tip');
    return response.data;
  },
};

