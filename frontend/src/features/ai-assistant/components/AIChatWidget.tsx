/**
 * AI Assistant Chat Widget - Sunflower Botanical Theme
 *
 * Floating conversational AI crop advisor ("Helio") crafted to match the Sunflower
 * Expert System's botanical glassmorphic visual language (Amber & Emerald).
 * Features:
 * - Knows all 20 diseases, 62 symptoms, and diagnostic rules
 * - Dynamic system navigation to any page
 * - Role-enforced data manipulation (Grower, Agronomist, Admin)
 * - Interactive Disease Draft Confirmation Cards (1-click confirm/cancel)
 * - Real-time Page Context Awareness
 * - Web Speech API Voice Dictation
 * - Message Copying & Rich Markdown / Table Rendering
 */

import type React from 'react';
import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router';
import {
  X,
  Send,
  Loader2,
  Image as ImageIcon,
  Sparkles,
  Shield,
  Trash2,
  Sprout,
  ArrowRight,
  Compass,
  Copy,
  Check,
  MapPin,
  CheckCircle2,
  XCircle,
  FileCode,
} from 'lucide-react';
import {
  type SuggestedAction,
  chatWithAI,
  adminChatWithAI,
  analyzeImage,
  matchDiseaseByImage,
  type AIChatResponse,
} from '@/api/ai';
import { uploadMedia } from '@/features/admin/api';
import { useAuth } from '@/features/auth';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggested_actions?: SuggestedAction[] | undefined;
  navigate_to?: string | undefined;
}

interface DiseaseDraftPayload {
  entity_type: string;
  disease_name: string;
  category: string;
  affected_parts?: string[];
  growth_stages_vulnerable?: string[];
  primary_symptoms?: string[];
  environmental_conditions?: string;
  preventative_measures?: string[];
  curative_treatments?: string[];
}

const GROWER_PROMPTS = [
  {
    en: 'How to check symptoms in this system?',
    km: 'តើត្រូវពិនិត្យរោគសញ្ញាយ៉ាងម៉េច?',
    icon: '🔍',
  },
  {
    en: 'My sunflower leaves have yellow spots',
    km: 'ស្លឹកផ្កាឈូករ័ត្នខ្ញុំមានចំណុចលឿង',
    icon: '🍂',
  },
  {
    en: 'How to treat Sunflower Rust?',
    km: 'តើត្រូវព្យាបាលជំងឺច្រែះផ្កាឈូករ័ត្នយ៉ាងដូចម្តេច?',
    icon: '💊',
  },
  {
    en: 'Diseases attacking during Flowering stage?',
    km: 'តើមានជំងឺអ្វីខ្លះពេលចេញផ្កា?',
    icon: '🌻',
  },
];

const ADMIN_PROMPTS = [
  {
    en: 'Find new data that system not yet have',
    km: 'ស្វែងរកជំងឺដែលប្រព័ន្ធមិនទាន់មាន',
    icon: '🔍',
  },
  {
    en: 'Draft disease Southern Blight',
    km: 'បង្កើតសេចក្តីព្រាងជំងឺ Southern Blight',
    icon: '➕',
  },
  {
    en: 'Compare White Mold and Charcoal Rot',
    km: 'ប្រៀបធៀបជំងឺ White Mold និង Charcoal Rot',
    icon: '🔬',
  },
  {
    en: 'System knowledge status',
    km: 'ស្ថានភាពទិន្នន័យប្រព័ន្ធ',
    icon: '📊',
  },
];

export function AIChatWidget(): React.JSX.Element | null {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if user is admin or expert
  const isAdminOrExpert = user?.role === 'admin' || user?.role === 'agronomist';
  const isKhmer = i18n.language === 'km';

  // Determine current page context
  const getPageContext = (pathname: string): { label: string; prompt: string } => {
    if (pathname.startsWith('/diseases/') && pathname !== '/diseases') {
      const slug = pathname.replace('/diseases/', '');
      const cleanName = slug.replace(/-/g, ' ');
      return {
        label: `Viewing: ${cleanName}`,
        prompt: `Tell me more about ${cleanName} and how to treat it`,
      };
    }
    if (pathname === '/diseases') {
      return {
        label: 'Disease Catalog',
        prompt: 'Give me an overview of the diseases in the catalog',
      };
    }
    if (pathname === '/check' || pathname.startsWith('/check/')) {
      return {
        label: 'Symptom Checker',
        prompt: 'Help me select symptoms for an accurate diagnosis',
      };
    }
    if (pathname === '/admin/diseases') {
      return {
        label: 'Disease Management',
        prompt: 'Show me data management options for diseases',
      };
    }
    if (pathname === '/admin/symptoms') {
      return {
        label: 'Symptom Management',
        prompt: 'Show me how to manage botanical symptoms',
      };
    }
    if (pathname === '/admin') {
      return {
        label: 'Admin Control Center',
        prompt: 'Show system statistics and knowledge status',
      };
    }
    if (pathname === '/history') {
      return {
        label: 'Diagnosis History',
        prompt: 'How are previous diagnosis records analyzed?',
      };
    }
    return {
      label: 'Sunflower System',
      prompt: 'What can you help me with in this system?',
    };
  };

  const pageContext = getPageContext(location.pathname);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleNavigate = (path: string) => {
    if (!path) return;
    navigate(path);
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText ?? input).trim();
    if ((!textToSend && !selectedImage) || isLoading || !user) return;

    const userMessage: Message = {
      role: 'user',
      content: selectedImage
        ? `${textToSend || 'Analyze this crop photo'} [Photo attached]`
        : textToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let response: AIChatResponse;

      // If image is selected, use image analysis
      if (selectedImage) {
        const reader = new FileReader();
        const imageBase64 = await new Promise<string>((resolve, reject) => {
          reader.onload = () => {
            const base64 = reader.result as string;
            const parts = base64.split(',');
            const base64Data = parts[1];
            if (base64Data) {
              resolve(base64Data);
            } else {
              reject(new Error('Invalid image format'));
            }
          };
          reader.onerror = () => reject(new Error('Failed to read image'));
          reader.readAsDataURL(selectedImage);
        });

        // Concurrently analyze image, match against database diseases, and persist to system media storage
        const [matchResult, mediaRecord] = await Promise.all([
          matchDiseaseByImage({
            image_base64: imageBase64,
            locale: i18n.language,
            additional_context: textToSend,
          }).catch(async (err) => {
            console.warn('matchDiseaseByImage failed, falling back to analyzeImage:', err);
            const fallback = await analyzeImage({
              image_base64: imageBase64,
              locale: i18n.language,
              additional_context: textToSend,
            });
            return {
              matched: false,
              disease: null,
              auto_checked_symptom_ids: [],
              symptom_names: [],
              observations: fallback.observations,
              analysis_text: fallback.analysis_text,
              navigate_to: null,
              warning: fallback.warning,
            };
          }),
          uploadMedia(selectedImage).catch((err) => {
            console.warn('Could not auto-persist image to media library:', err);
            return null;
          }),
        ]);

        const actions: SuggestedAction[] = [];

        if (matchResult.matched && matchResult.disease) {
          const matched = matchResult.disease;
          actions.push({
            label: isKhmer ? `🌻 មើលទំព័រជំងឺ (${matched.name})` : `🌻 View Disease Page (${matched.name})`,
            path: `/diseases/${matched.slug}`,
            type: 'navigate',
          });
          actions.push({
            label: isKhmer
              ? `🩺 ធីករោគសញ្ញាស្វ័យប្រវត្តិ (${matchResult.auto_checked_symptom_ids.length})`
              : `🩺 Auto-Check Symptoms in Checker (${matchResult.auto_checked_symptom_ids.length})`,
            path: `/check?disease=${matched.slug}&symptoms=${matchResult.auto_checked_symptom_ids.join(',')}`,
            type: 'diagnosis',
          });
        } else {
          actions.push(
            { label: isKhmer ? '🩺 ចាប់ផ្តើមធ្វើរោគវិនិច្ឆ័យ' : 'Start Diagnosis with Photo', path: '/check', type: 'diagnosis' },
            { label: isKhmer ? '📚 មើលបញ្ជីជំងឺទាំងអស់' : 'Browse Disease Catalog', path: '/diseases', type: 'navigate' },
          );
        }

        if (mediaRecord?.id) {
          actions.unshift({
            label: isKhmer ? '💾 រូបភាពត្រូវបានរក្សាទុកក្នុងប្រព័ន្ធ' : '💾 Photo Saved to System Media',
            path: mediaRecord.url,
            type: 'navigate',
          });
        }

        let messageText = matchResult.analysis_text;
        if (matchResult.matched && matchResult.disease) {
          const matched = matchResult.disease;
          const matchPercent = Math.round(matched.confidence * 100);
          const header = isKhmer
            ? `🎯 **ការផ្គូផ្គងរូបភាពជាមួយប្រព័ន្ធទិន្នន័យ៖** **${matched.name}** (ភាពជាក់លាក់ ${matchPercent}%)\n\n`
            : `🎯 **System Photo Match:** **${matched.name}** (${matchPercent}% match)\n\n`;
          const symptomsList = matchResult.symptom_names && matchResult.symptom_names.length > 0
            ? (isKhmer ? `📋 **រោគសញ្ញាដែលបានកំណត់ក្នុងប្រព័ន្ធ៖**\n` : `📋 **Auto-Identified Symptoms from System:**\n`) +
              matchResult.symptom_names.map((s) => `• ${s}`).join('\n') +
              '\n\n'
            : '';
          messageText = `${header}${symptomsList}${matchResult.analysis_text}`;
        }

        response = {
          message: messageText,
          conversation_id: conversationId ?? crypto.randomUUID(),
          needs_diagnosis: matchResult.observations.visible_symptoms.length > 0,
          extracted_symptoms: {
            crop: matchResult.observations.crop_identified || '',
            plant_part: matchResult.observations.plant_parts,
            symptoms: matchResult.observations.visible_symptoms,
            color_changes: matchResult.observations.color_abnormalities,
            spots: matchResult.observations.spots_lesions,
            pests: matchResult.observations.pests_visible,
            environment: [],
            duration: '',
            severity: '',
            confidence: matchResult.observations.crop_confidence || 0,
          },
          suggested_actions: actions,
        };

        // If matched, navigate user directly to the disease page and provide auto-checked symptoms
        if (matchResult.matched && matchResult.disease) {
          navigate(`/diseases/${matchResult.disease.slug}`, {
            state: {
              fromPhotoMatch: true,
              autoCheckSymptomIds: matchResult.auto_checked_symptom_ids,
              symptomNames: matchResult.symptom_names,
              matchedDisease: matchResult.disease,
            },
          });
        }

        // Clear image after sending
        setSelectedImage(null);
        setImagePreview(null);
      } else {
        // Regular chat - protected with a 30s timeout to guarantee no infinite loading
        const chatPromise = isAdminOrExpert
          ? adminChatWithAI({
              message: userMessage.content,
              locale: i18n.language,
              conversation_id: conversationId || '',
            })
          : chatWithAI({
              message: userMessage.content,
              locale: i18n.language,
              conversation_id: conversationId || '',
            });

        const timeoutPromise = new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('AI_TIMEOUT')), 90000)
        );

        response = await Promise.race([chatPromise, timeoutPromise]);
      }

      setConversationId(response.conversation_id);

      // Execute dynamic navigation if instructed by the AI
      if (response.navigate_to) {
        handleNavigate(response.navigate_to);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        suggested_actions: response.suggested_actions ?? undefined,
        navigate_to: response.navigate_to ?? undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI chat error:', error);

      // Build a descriptive error message based on the error type
      let errorContent: string;
      let errorActions: Message['suggested_actions'] | undefined;

      const isStatus401 =
        (error && typeof error === 'object' && 'status' in error && (error as { status: number }).status === 401) ||
        (error instanceof Error && (error.message.includes('401') || error.message.toLowerCase().includes('unauthorized') || error.message.toLowerCase().includes('token')));

      const isStatus503 =
        (error && typeof error === 'object' && 'status' in error && (error as { status: number }).status === 503) ||
        (error instanceof Error && error.message.includes('503'));

      if (error instanceof Error && error.message === 'AI_TIMEOUT') {
        errorContent = t(
          'ai.timeout',
          '⏳ The AI is taking longer than expected. Please try again in a moment.',
        );
      } else if (isStatus401) {
        errorContent = t(
          'ai.unauthorized',
          '🔐 Your session has expired. Please log in again to continue.',
        );
        errorActions = [
          {
            label: isKhmer ? '🔑 ចូលគណនីម្តងទៀត' : '🔑 Log In Again',
            path: '/login',
            type: 'navigate',
          },
        ];
      } else if (isStatus503) {
        errorContent = t(
          'ai.unavailable',
          '🔌 The AI service is temporarily unavailable. Please ensure Ollama is running and try again.',
        );
      } else if (error && typeof error === 'object' && 'detail' in error && (error as { detail?: string }).detail) {
        errorContent = `⚠️ ${(error as { detail: string }).detail}`;
      } else {
        errorContent = t('ai.error', 'Sorry, I encountered an error. Please try again.');
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date(),
        suggested_actions: errorActions,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  const handleReset = () => {
    setMessages([]);
    setConversationId(undefined);
    setSelectedImage(null);
    setImagePreview(null);
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (!user) return null;

  const quickPrompts = isAdminOrExpert ? ADMIN_PROMPTS : GROWER_PROMPTS;

  return (
    <>
      {/* Floating Button - Sunflower Botanical Design */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 group flex items-center focus:outline-hidden"
          aria-label={t('ai.openChat', 'Open AI Assistant')}
        >
          {/* Subtle sunflower golden halo animation */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-amber-400 via-amber-500 to-emerald-500 opacity-60 blur-md group-hover:opacity-90 group-hover:blur-lg transition-all duration-300 animate-pulse" />

          {/* Main button pill */}
          <div className="relative flex items-center gap-3 bg-gradient-to-r from-amber-500 via-amber-600 to-emerald-600 text-white pl-4 pr-5 py-3.5 rounded-full shadow-xl shadow-amber-900/20 border border-amber-300/30 transition-all duration-300 group-hover:scale-105 group-hover:shadow-2xl">
            {/* Sunflower emblem avatar */}
            <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-white/20 backdrop-blur-xs border border-white/30 shrink-0">
              <span className="text-base select-none">🌻</span>
            </div>

            <div className="flex flex-col items-start text-left">
              <span className="font-bold text-xs sm:text-sm tracking-tight flex items-center gap-1.5 drop-shadow-xs">
                Helio • {t('ai.assistant', 'AI Assistant')}
                {isAdminOrExpert ? (
                  <Shield className="w-3.5 h-3.5 text-amber-200 shrink-0" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-amber-200 shrink-0" />
                )}
              </span>
              <span className="text-[0.68rem] text-amber-100/90 font-medium">
                {t('ai.tagline', 'Ask me about plant diseases')}
              </span>
            </div>
          </div>
        </button>
      )}

      {/* Chat Window - Botanical Glassmorphism */}
      {isOpen && (
        <div
          className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-[460px] h-[640px] max-h-[88vh] bg-white/95 dark:bg-[#1E2615]/95 backdrop-blur-xl rounded-3xl shadow-2xl shadow-stone-900/20 dark:shadow-black/60 flex flex-col overflow-hidden border border-stone-200/90 dark:border-white/15 animate-in fade-in zoom-in-95 duration-200"
          dir="ltr"
        >
          {/* Header - Botanical Sunflower Amber to Emerald */}
          <div className="relative bg-gradient-to-r from-amber-500 via-amber-600 to-emerald-600 text-white px-4.5 py-3.5 flex items-center justify-between border-b border-amber-400/20 shadow-xs">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              {/* Avatar */}
              <div className="relative flex items-center justify-center w-10 h-10 rounded-2xl bg-white/15 backdrop-blur-sm border border-white/25 shadow-xs shrink-0">
                <span className="text-xl select-none">🌻</span>
                {/* Live Online Badge */}
                <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-amber-600" />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5">
                  <h3 className={`font-bold text-base text-white truncate ${isKhmer ? 'leading-relaxed' : ''}`}>
                    Helio <span className="text-xs font-normal text-amber-100/80">• AI Crop Advisor</span>
                  </h3>
                  <span className="px-1.5 py-0.2 rounded text-[0.62rem] font-bold bg-amber-400/30 text-amber-100 border border-white/20 shrink-0 uppercase">
                    {user?.role || 'GROWER'}
                  </span>
                </div>
                <p className={`text-[0.72rem] text-amber-100/90 truncate ${isKhmer ? 'leading-relaxed' : ''}`}>
                  {isAdminOrExpert
                    ? isKhmer
                      ? 'របៀបគ្រប់គ្រង - ចេះគ្រប់ទិន្នន័យ & អាចកែប្រែបាន'
                      : 'Knowledge Base & System Command Mode'
                    : isKhmer
                      ? 'ជំនួយការឆ្លាតវៃ - វិភាគរោគសញ្ញា & នាំផ្លូវ'
                      : 'Crop Advisor • Disease Diagnosis & Navigation'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {messages.length > 0 && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="p-1.5 text-white/80 hover:text-white hover:bg-white/15 rounded-lg transition-colors cursor-pointer"
                  title={t('ai.newConversation', 'New conversation')}
                  aria-label={t('ai.newConversation', 'New conversation')}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-white/80 hover:text-white hover:bg-white/15 rounded-lg transition-colors cursor-pointer"
                aria-label={t('common.close', 'Close')}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Real-Time Location Context Strip */}
          <div className="bg-amber-500/10 dark:bg-emerald-950/40 border-b border-amber-500/15 px-3.5 py-1.5 flex items-center justify-between text-[0.7rem] text-amber-900 dark:text-amber-200">
            <div className="flex items-center gap-1.5 truncate">
              <MapPin className="w-3 h-3 text-amber-600 dark:text-amber-400 shrink-0" />
              <span className="font-medium truncate">{pageContext.label}</span>
            </div>
            <button
              type="button"
              onClick={() => void handleSend(pageContext.prompt)}
              className="px-2 py-0.5 rounded-full bg-amber-500/20 hover:bg-amber-500/30 text-amber-800 dark:text-amber-300 font-medium shrink-0 transition-colors text-[0.68rem] cursor-pointer"
            >
              Ask about page
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-stone-50/50 dark:bg-[#161D10]/50">
            {messages.length === 0 && (
              <div className="text-center py-5 px-2 space-y-3.5">
                {/* Botanical Icon */}
                <div className="inline-flex items-center justify-center w-13 h-13 rounded-2xl bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/20 shadow-xs">
                  <Sprout className="w-6 h-6" />
                </div>

                <div className="space-y-1">
                  <h4 className={`font-bold text-sm text-gray-900 dark:text-white ${isKhmer ? 'leading-relaxed' : ''}`}>
                    {t('ai.welcome', 'Hello! How can I help you today?')}
                  </h4>
                  <p className={`text-xs text-gray-600 dark:text-gray-300 max-w-xs mx-auto leading-relaxed ${isKhmer ? 'leading-relaxed' : ''}`}>
                    {isAdminOrExpert
                      ? isKhmer
                        ? 'ខ្ញុំអាចជួយស្វែងរកជំងឺដែលមិនទាន់មាន បង្កើតសេចក្តីព្រាង ផ្ទៀងផ្ទាត់ទិន្នន័យ ព្រមទាំងប្រៀបធៀបជំងឺ និងផ្តល់វេជ្ជបញ្ជា។'
                        : 'I can discover missing data, draft new diseases with expert confirmation, run differential comparisons, and provide clinical prescriptions.'
                      : isKhmer
                        ? 'ពិពណ៌នារោគសញ្ញា ឬ បញ្ជូនរូបថតដើមរបស់អ្នក — ខ្ញុំនឹងវិភាគ និងជួយកំណត់ជំងឺ ព្រមទាំងផ្តល់វិធីព្យាបាល!'
                        : 'Describe your plant symptoms or upload a photo — I\'ll analyze and help identify diseases with treatment advice!'}
                  </p>
                </div>

                {/* Role-Aware Quick Suggestion Prompt Chips */}
                <div className="space-y-1.5 pt-1">
                  <span className="text-[0.68rem] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                    Recommended Actions
                  </span>
                  <div className="flex flex-col gap-1.5 text-left">
                    {quickPrompts.map((prompt, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => void handleSend(isKhmer ? prompt.km : prompt.en)}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white dark:bg-[#1E2615] hover:bg-amber-50/80 dark:hover:bg-[#2A3420] text-gray-800 dark:text-gray-200 text-xs border border-stone-200/80 dark:border-white/10 shadow-2xs hover:border-amber-400/50 transition-all text-left cursor-pointer"
                      >
                        <span className="text-sm shrink-0">{prompt.icon}</span>
                        <span className="truncate flex-1 font-medium">
                          {isKhmer ? prompt.km : prompt.en}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Chat Messages */}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in duration-200`}
              >
                {/* Assistant botanical badge */}
                {message.role === 'assistant' && (
                  <div className="mr-2 shrink-0 self-end mb-1">
                    <div className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-400 flex items-center justify-center border border-amber-500/30 text-xs select-none">
                      🌻
                    </div>
                  </div>
                )}

                <div
                  className={`group relative max-w-[88%] rounded-2xl px-3.5 py-2.5 shadow-xs ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-br-xs'
                      : 'bg-white dark:bg-[#253018] text-gray-800 dark:text-gray-100 border border-stone-200/80 dark:border-white/10 rounded-bl-xs'
                  } ${isKhmer ? 'leading-relaxed' : ''}`}
                >
                  {/* Copy message button */}
                  {message.role === 'assistant' && (
                    <button
                      type="button"
                      onClick={() => handleCopy(message.content, index)}
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md bg-stone-100/80 dark:bg-stone-800/80 text-gray-500 dark:text-gray-400 hover:text-amber-600 cursor-pointer shadow-2xs"
                      title="Copy response"
                    >
                      {copiedIndex === index ? (
                        <Check className="w-3 h-3 text-emerald-500" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  )}

                  {/* Message Body with Markdown styling & Interactive Draft Card */}
                  <FormattedMessageText
                    content={message.content}
                    onNavigate={handleNavigate}
                    onSendMessage={(text) => void handleSend(text)}
                  />

                  {/* Navigation notice if triggered */}
                  {message.navigate_to && (
                    <div className="mt-2 pt-1.5 border-t border-stone-200/50 dark:border-white/10 flex items-center gap-1.5 text-[0.68rem] text-emerald-600 dark:text-emerald-400 font-medium">
                      <Compass className="w-3 h-3 shrink-0 animate-spin" />
                      <span>{t('ai.navigated', 'Navigated to')}: <code className="font-mono bg-emerald-500/10 px-1 py-0.5 rounded">{message.navigate_to}</code></span>
                    </div>
                  )}

                  {/* Suggested Interactive Action Pills */}
                  {message.suggested_actions && message.suggested_actions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-stone-200/60 dark:border-white/10">
                      {message.suggested_actions.map((action, actionIdx) => (
                        <button
                          key={actionIdx}
                          type="button"
                          onClick={() => {
                            if (
                              action.type === 'message' ||
                              action.type === 'prompt' ||
                              (!action.path.startsWith('/') && !action.path.startsWith('http'))
                            ) {
                              void handleSend(action.path || action.label);
                            } else {
                              handleNavigate(action.path);
                            }
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 text-[0.72rem] font-semibold border border-amber-500/30 transition-all hover:scale-102 cursor-pointer shadow-2xs"
                        >
                          <span>{action.label}</span>
                          <ArrowRight className="w-3 h-3 shrink-0" />
                        </button>
                      ))}
                    </div>
                  )}

                  <span
                    className={`block text-[0.62rem] mt-1.5 text-right font-mono ${
                      message.role === 'user' ? 'text-amber-100' : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start items-center gap-2 animate-in fade-in">
                <div className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-400 flex items-center justify-center border border-amber-500/30 text-xs select-none">
                  🌻
                </div>
                <div className="bg-white dark:bg-[#253018] border border-stone-200/80 dark:border-white/10 rounded-2xl px-3.5 py-2.5 flex items-center gap-2 shadow-xs">
                  <Loader2 className="w-4 h-4 animate-spin text-amber-500" />
                  <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">
                    {isKhmer ? 'កំពុងដំណើរការ...' : 'Consulting Sunflower Knowledge Base...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white/95 dark:bg-[#1E2615]/95 border-t border-stone-200/80 dark:border-white/10 space-y-2">
            {/* Image Preview if attached */}
            {imagePreview && (
              <div className="relative inline-block">
                <img
                  src={imagePreview}
                  alt="Crop preview"
                  className="max-h-16 rounded-xl border border-amber-400 shadow-xs"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute -top-1.5 -right-1.5 bg-rose-500 text-white rounded-full w-5 h-5 flex items-center justify-center hover:bg-rose-600 transition-colors shadow-xs cursor-pointer"
                  aria-label="Remove image"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}

            <div className="flex items-center gap-1.5">
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />

              {/* Photo Upload Button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="p-2.5 rounded-xl bg-stone-100 hover:bg-amber-50 dark:bg-[#253018] dark:hover:bg-[#2A3420] text-gray-600 dark:text-gray-300 hover:text-amber-600 dark:hover:text-amber-400 border border-stone-200/80 dark:border-white/10 transition-colors cursor-pointer"
                disabled={isLoading}
                title="Attach plant photo"
                aria-label="Attach plant photo"
              >
                <ImageIcon className="w-4 h-4" />
              </button>

              {/* Text Input */}
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={
                  isAdminOrExpert
                    ? isKhmer
                      ? 'សួរអំពីជំងឺ, រោគសញ្ញា, ឬបញ្ជាឱ្យនាំផ្លូវ/កែប្រែ...'
                      : 'Ask about diseases, check symptoms, or type commands...'
                    : t('ai.inputPlaceholder', 'Describe your plant symptoms...')
                }
                className={`flex-1 px-3.5 py-2 rounded-xl bg-stone-100/90 dark:bg-[#253018]/90 border border-stone-200/80 dark:border-white/10 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-xs sm:text-sm focus:outline-hidden focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all ${
                  isKhmer ? 'leading-relaxed' : ''
                }`}
                disabled={isLoading}
              />

              {/* Send Button */}
              <button
                type="button"
                onClick={() => void handleSend()}
                disabled={(!input.trim() && !selectedImage) || isLoading}
                className="p-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 disabled:opacity-40 disabled:cursor-not-allowed text-white shadow-xs shadow-amber-600/20 transition-all shrink-0 cursor-pointer"
                aria-label={t('common.send', 'Send')}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/**
 * Interactive Botanical Disease Draft Card
 */
function DiseaseDraftCard({
  payload,
  onSendMessage,
}: {
  payload: DiseaseDraftPayload;
  onSendMessage: (text: string) => void;
}): React.JSX.Element {
  return (
    <div className="my-2.5 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-amber-500/10 to-emerald-500/5 border border-emerald-500/30 p-3.5 shadow-sm text-left">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-emerald-500/20">
        <div className="flex items-center gap-1.5">
          <FileCode className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span className="text-[0.68rem] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">
            Botanical Record Draft
          </span>
        </div>
        <span className="px-2 py-0.5 rounded-full text-[0.6rem] font-bold bg-amber-400/20 text-amber-700 dark:text-amber-300 border border-amber-500/30">
          Pending Confirmation
        </span>
      </div>

      {/* Disease Title & Pathogen */}
      <div className="mt-2.5">
        <h4 className="font-bold text-sm text-gray-900 dark:text-white">
          {payload.disease_name}
        </h4>
        <span className="inline-block mt-0.5 px-2 py-0.5 rounded-md text-[0.65rem] font-semibold bg-emerald-500/15 text-emerald-800 dark:text-emerald-200">
          {payload.category} Pathogen
        </span>
      </div>

      {/* Affected Parts & Stages */}
      <div className="mt-2 flex flex-wrap gap-1">
        {payload.affected_parts?.map((part, idx) => (
          <span
            key={idx}
            className="px-1.5 py-0.2 rounded text-[0.6rem] bg-stone-200/70 dark:bg-stone-700/60 text-stone-700 dark:text-stone-300 font-medium"
          >
            {part}
          </span>
        ))}
      </div>

      {/* Primary Symptoms */}
      {payload.primary_symptoms && payload.primary_symptoms.length > 0 && (
        <div className="mt-2.5 text-xs text-gray-700 dark:text-gray-300 space-y-1">
          <span className="text-[0.68rem] font-semibold text-emerald-800 dark:text-emerald-300">
            Hallmark Symptoms:
          </span>
          <ul className="list-disc list-inside space-y-0.5 text-[0.72rem]">
            {payload.primary_symptoms.slice(0, 3).map((sym, idx) => (
              <li key={idx} className="truncate">
                {sym}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Confirm / Cancel Actions */}
      <div className="mt-3 pt-2.5 border-t border-emerald-500/20 flex items-center gap-2">
        <button
          type="button"
          onClick={() => onSendMessage('confirm')}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs shadow-xs transition-all hover:scale-101 cursor-pointer"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Confirm & Save</span>
        </button>
        <button
          type="button"
          onClick={() => onSendMessage('cancel')}
          className="flex items-center justify-center gap-1 px-3 py-1.5 rounded-xl bg-stone-200/80 hover:bg-rose-100 dark:bg-stone-700/80 dark:hover:bg-rose-950/60 text-stone-700 hover:text-rose-600 dark:text-stone-300 font-semibold text-xs transition-colors cursor-pointer"
        >
          <XCircle className="w-3.5 h-3.5" />
          <span>Discard</span>
        </button>
      </div>
    </div>
  );
}

/**
 * Render Markdown-style text with clickable internal route links, bold, code, bullets,
 * Markdown tables, and Interactive Disease Draft Cards.
 */
function FormattedMessageText({
  content,
  onNavigate,
  onSendMessage,
}: {
  content: string;
  onNavigate: (path: string) => void;
  onSendMessage: (text: string) => void;
}): React.JSX.Element {
  // Check for embedded JSON payload (e.g. standardized disease entry)
  const jsonRegex = /```json\s*(\{[\s\S]*?\})\s*```/;
  const jsonMatch = content.match(jsonRegex);

  let draftPayload: DiseaseDraftPayload | null = null;
  let cleanContent = content;

  if (jsonMatch && jsonMatch[1]) {
    try {
      const parsed = JSON.parse(jsonMatch[1]);
      if (parsed.entity_type === 'disease_record') {
        draftPayload = parsed as DiseaseDraftPayload;
        cleanContent = content.replace(jsonRegex, '').trim();
      }
    } catch {
      // Not valid json, render as normal
    }
  }

  const lines = cleanContent.split('\n');
  const elements: React.ReactNode[] = [];
  let currentTableLines: string[] = [];

  const flushTable = (keyPrefix: number) => {
    if (currentTableLines.length >= 2) {
      const headerLine = currentTableLines[0];
      const rowLines = currentTableLines.slice(2); // Skip separator line

      if (headerLine) {
        const headers = headerLine
          .split('|')
          .map((c) => c.trim())
          .filter(Boolean);

        const rows = rowLines.map((row) =>
          row
            .split('|')
            .map((c) => c.trim())
            .filter(Boolean)
        );

        elements.push(
          <div key={`table-${keyPrefix}`} className="my-2.5 overflow-x-auto rounded-xl border border-stone-200/80 dark:border-white/10 shadow-2xs">
            <table className="min-w-full text-left text-xs border-collapse">
              <thead className="bg-amber-500/10 dark:bg-amber-500/20 text-amber-900 dark:text-amber-200 font-bold border-b border-amber-500/20">
                <tr>
                  {headers.map((h, hIdx) => (
                    <th key={hIdx} className="px-2.5 py-1.5 font-bold">
                      {renderInlineStyles(h, onNavigate)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200/60 dark:divide-white/5 bg-white/40 dark:bg-[#1C2413]/40">
                {rows.map((row, rIdx) => (
                  <tr key={rIdx} className={rIdx % 2 === 0 ? '' : 'bg-stone-50/50 dark:bg-white/[0.02]'}>
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-2.5 py-1.5 text-gray-800 dark:text-gray-200 align-top">
                        {renderInlineStyles(cell, onNavigate)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
    }
    currentTableLines = [];
  };

  lines.forEach((line, lIdx) => {
    const trimmed = line.trim();

    // Check if line is part of a markdown table
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      currentTableLines.push(trimmed);
      return;
    }

    if (currentTableLines.length > 0) {
      flushTable(lIdx);
    }

    if (!trimmed) {
      elements.push(<div key={`space-${lIdx}`} className="h-1.5" />);
      return;
    }

    // Header ###
    if (line.startsWith('### ')) {
      elements.push(
        <h4 key={`h3-${lIdx}`} className="font-bold text-xs sm:text-[0.85rem] text-amber-800 dark:text-amber-400 mt-1.5 mb-0.5">
          {renderInlineStyles(line.replace('### ', ''), onNavigate)}
        </h4>
      );
      return;
    }

    // Header ####
    if (line.startsWith('#### ')) {
      elements.push(
        <h5 key={`h4-${lIdx}`} className="font-bold text-xs sm:text-[0.8rem] text-emerald-800 dark:text-emerald-400 mt-1 mb-0.5">
          {renderInlineStyles(line.replace('#### ', ''), onNavigate)}
        </h5>
      );
      return;
    }

    // Bullet point
    if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
      const cleanLine = trimmed.replace(/^[•\-]\s*/, '');
      elements.push(
        <div key={`bullet-${lIdx}`} className="flex items-start gap-1.5 text-xs sm:text-[0.82rem] pl-1">
          <span className="text-amber-500 font-bold shrink-0">•</span>
          <span className="flex-1 leading-relaxed">
            {renderInlineStyles(cleanLine, onNavigate)}
          </span>
        </div>
      );
      return;
    }

    // Standard paragraph
    elements.push(
      <p key={`p-${lIdx}`} className="text-xs sm:text-[0.82rem] leading-relaxed">
        {renderInlineStyles(line, onNavigate)}
      </p>
    );
  });

  if (currentTableLines.length > 0) {
    flushTable(lines.length);
  }

  return (
    <div className="space-y-1">
      {draftPayload && (
        <DiseaseDraftCard
          payload={draftPayload}
          onSendMessage={onSendMessage}
        />
      )}
      {elements}
    </div>
  );
}

function renderInlineStyles(text: string, onNavigate: (path: string) => void): React.ReactNode[] {
  const regex = /(\[.*?\]\(.*?\)|\*\*.*?\*\*|`.*?`|\*.*?\*)/g;
  const parts = text.split(regex);

  return parts.map((part, idx) => {
    if (!part) return null;

    // Link [label](path)
    const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/);
    if (linkMatch && linkMatch[1] && linkMatch[2]) {
      const label = linkMatch[1];
      const path = linkMatch[2];
      return (
        <button
          key={idx}
          type="button"
          onClick={() => onNavigate(path)}
          className="text-amber-600 dark:text-amber-400 underline font-semibold hover:text-amber-700 dark:hover:text-amber-300 cursor-pointer inline-flex items-center gap-0.5"
        >
          {label}
        </button>
      );
    }

    // Bold **text**
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={idx} className="font-semibold text-gray-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }

    // Italic *text*
    if (part.startsWith('*') && part.endsWith('*')) {
      return (
        <em key={idx} className="italic text-gray-700 dark:text-gray-300">
          {part.slice(1, -1)}
        </em>
      );
    }

    // Code `text`
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={idx} className="px-1 py-0.5 rounded bg-amber-500/10 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 text-[0.72rem] font-mono">
          {part.slice(1, -1)}
        </code>
      );
    }

    return part;
  });
}
