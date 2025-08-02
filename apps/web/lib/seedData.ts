// Comprehensive seed data for Seraaj v2 demo

export interface Organization {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  logo: string;
  website: string;
  email: string;
  location: string;
  locationAr: string;
  country: string;
  countryAr: string;
  causes: string[];
  established: number;
  teamSize: string;
  verified: boolean;
  rating: number;
  totalOpportunities: number;
  activeOpportunities: number;
  totalVolunteers: number;
}

export interface Volunteer {
  id: string;
  name: string;
  nameAr: string;
  email: string;
  avatar: string;
  location: string;
  locationAr: string;
  country: string;
  countryAr: string;
  bio: string;
  bioAr: string;
  skills: string[];
  interests: string[];
  languages: string[];
  availability: 'full-time' | 'part-time' | 'weekends' | 'flexible';
  experience: 'beginner' | 'intermediate' | 'expert';
  joinDate: string;
  completedOpportunities: number;
  rating: number;
  verified: boolean;
}

export interface Opportunity {
  id: string;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  organizationId: string;
  organizationName: string;
  organizationLogo: string;
  location: string;
  locationAr: string;
  country: string;
  countryAr: string;
  remote: boolean;
  causes: string[];
  skillsRequired: string[];
  timeCommitment: string;
  duration: string;
  urgency: 'low' | 'medium' | 'high';
  volunteersNeeded: number;
  volunteersApplied: number;
  volunteersAccepted: number;
  status: 'active' | 'filled' | 'closed' | 'draft';
  postedDate: string;
  applicationDeadline: string;
  startDate: string;
  requirements: string[];
  benefits: string[];
  images: string[];
  featured: boolean;
  verified: boolean;
}

export const MENA_COUNTRIES = [
  { en: 'Jordan', ar: 'الأردن' },
  { en: 'Lebanon', ar: 'لبنان' },
  { en: 'Egypt', ar: 'مصر' },
  { en: 'UAE', ar: 'الإمارات' },
  { en: 'Saudi Arabia', ar: 'السعودية' },
  { en: 'Morocco', ar: 'المغرب' },
  { en: 'Tunisia', ar: 'تونس' },
  { en: 'Palestine', ar: 'فلسطين' },
  { en: 'Iraq', ar: 'العراق' },
  { en: 'Syria', ar: 'سوريا' }
];

export const MAJOR_CITIES = {
  'Jordan': [
    { en: 'Amman', ar: 'عمان' },
    { en: 'Irbid', ar: 'إربد' },
    { en: 'Zarqa', ar: 'الزرقاء' }
  ],
  'Lebanon': [
    { en: 'Beirut', ar: 'بيروت' },
    { en: 'Tripoli', ar: 'طرابلس' },
    { en: 'Sidon', ar: 'صيدا' }
  ],
  'Egypt': [
    { en: 'Cairo', ar: 'القاهرة' },
    { en: 'Alexandria', ar: 'الإسكندرية' },
    { en: 'Giza', ar: 'الجيزة' }
  ],
  'UAE': [
    { en: 'Dubai', ar: 'دبي' },
    { en: 'Abu Dhabi', ar: 'أبوظبي' },
    { en: 'Sharjah', ar: 'الشارقة' }
  ],
  'Saudi Arabia': [
    { en: 'Riyadh', ar: 'الرياض' },
    { en: 'Jeddah', ar: 'جدة' },
    { en: 'Dammam', ar: 'الدمام' }
  ]
};

export const CAUSES = [
  { en: 'Education', ar: 'التعليم' },
  { en: 'Health', ar: 'الصحة' },
  { en: 'Environment', ar: 'البيئة' },
  { en: 'Youth Development', ar: 'تطوير الشباب' },
  { en: 'Women Empowerment', ar: 'تمكين المرأة' },
  { en: 'Refugees', ar: 'اللاجئون' },
  { en: 'Community Development', ar: 'تطوير المجتمع' },
  { en: 'Technology', ar: 'التكنولوجيا' },
  { en: 'Arts & Culture', ar: 'الفنون والثقافة' },
  { en: 'Social Justice', ar: 'العدالة الاجتماعية' }
];

export const SKILLS = [
  { en: 'Teaching', ar: 'التدريس' },
  { en: 'Marketing', ar: 'التسويق' },
  { en: 'Graphic Design', ar: 'التصميم الجرافيكي' },
  { en: 'Web Development', ar: 'تطوير المواقع' },
  { en: 'Social Media', ar: 'وسائل التواصل الاجتماعي' },
  { en: 'Project Management', ar: 'إدارة المشاريع' },
  { en: 'Fundraising', ar: 'جمع التبرعات' },
  { en: 'Public Speaking', ar: 'الخطابة العامة' },
  { en: 'Data Analysis', ar: 'تحليل البيانات' },
  { en: 'Photography', ar: 'التصوير الفوتوغرافي' },
  { en: 'Translation', ar: 'الترجمة' },
  { en: 'Event Planning', ar: 'تنظيم الفعاليات' },
  { en: 'Counseling', ar: 'الإرشاد' },
  { en: 'Research', ar: 'البحث' },
  { en: 'Healthcare', ar: 'الرعاية الصحية' }
];

// Sample Organizations
export const SEED_ORGANIZATIONS: Organization[] = [
  {
    id: 'org-1',
    name: 'Hope Foundation Jordan',
    nameAr: 'مؤسسة الأمل الأردنية',
    description: 'Empowering communities through education and youth development programs across Jordan.',
    descriptionAr: 'تمكين المجتمعات من خلال برامج التعليم وتطوير الشباب في جميع أنحاء الأردن.',
    logo: '/logos/hope-foundation.png',
    website: 'https://hopefoundation.jo',
    email: 'info@hopefoundation.jo',
    location: 'Amman',
    locationAr: 'عمان',
    country: 'Jordan',
    countryAr: 'الأردن',
    causes: ['Education', 'Youth Development'],
    established: 2018,
    teamSize: '25-50',
    verified: true,
    rating: 4.8,
    totalOpportunities: 45,
    activeOpportunities: 12,
    totalVolunteers: 234
  },
  {
    id: 'org-2',
    name: 'Green Lebanon Initiative',
    nameAr: 'مبادرة لبنان الأخضر',
    description: 'Leading environmental conservation efforts and sustainability education throughout Lebanon.',
    descriptionAr: 'قيادة جهود الحفاظ على البيئة والتعليم المستدام في جميع أنحاء لبنان.',
    logo: '/logos/green-lebanon.png',
    website: 'https://greenlebanon.org',
    email: 'contact@greenlebanon.org',
    location: 'Beirut',
    locationAr: 'بيروت',
    country: 'Lebanon',
    countryAr: 'لبنان',
    causes: ['Environment', 'Education'],
    established: 2015,
    teamSize: '10-25',
    verified: true,
    rating: 4.6,
    totalOpportunities: 32,
    activeOpportunities: 8,
    totalVolunteers: 156
  },
  {
    id: 'org-3',
    name: 'Cairo Medical Aid',
    nameAr: 'المساعدة الطبية القاهرة',
    description: 'Providing healthcare access and medical education to underserved communities in Egypt.',
    descriptionAr: 'توفير الوصول إلى الرعاية الصحية والتعليم الطبي للمجتمعات المحرومة في مصر.',
    logo: '/logos/cairo-medical.png',
    website: 'https://cairomedical.org',
    email: 'info@cairomedical.org',
    location: 'Cairo',
    locationAr: 'القاهرة',
    country: 'Egypt',
    countryAr: 'مصر',
    causes: ['Health', 'Community Development'],
    established: 2012,
    teamSize: '50-100',
    verified: true,
    rating: 4.9,
    totalOpportunities: 67,
    activeOpportunities: 18,
    totalVolunteers: 389
  },
  {
    id: 'org-4',
    name: 'Tech for Good MENA',
    nameAr: 'التكنولوجيا من أجل الخير - المنطقة العربية',
    description: 'Bridging the digital divide through technology education and innovation across MENA.',
    descriptionAr: 'سد الفجوة الرقمية من خلال التعليم التكنولوجي والابتكار في المنطقة العربية.',
    logo: '/logos/tech-for-good.png',
    website: 'https://techforgood.mena',
    email: 'hello@techforgood.mena',
    location: 'Dubai',
    locationAr: 'دبي',
    country: 'UAE',
    countryAr: 'الإمارات',
    causes: ['Technology', 'Education', 'Youth Development'],
    established: 2020,
    teamSize: '10-25',
    verified: true,
    rating: 4.7,
    totalOpportunities: 28,
    activeOpportunities: 9,
    totalVolunteers: 127
  },
  {
    id: 'org-5',
    name: 'Women Rise Saudi',
    nameAr: 'نهوض المرأة السعودية',
    description: 'Empowering women through entrepreneurship training and professional development programs.',
    descriptionAr: 'تمكين المرأة من خلال تدريب ريادة الأعمال وبرامج التطوير المهني.',
    logo: '/logos/women-rise.png',
    website: 'https://womenrise.sa',
    email: 'contact@womenrise.sa',
    location: 'Riyadh',
    locationAr: 'الرياض',
    country: 'Saudi Arabia',
    countryAr: 'السعودية',
    causes: ['Women Empowerment', 'Education'],
    established: 2019,
    teamSize: '25-50',
    verified: true,
    rating: 4.5,
    totalOpportunities: 23,
    activeOpportunities: 7,
    totalVolunteers: 98
  }
];

// Sample Volunteers
export const SEED_VOLUNTEERS: Volunteer[] = [
  {
    id: 'vol-1',
    name: 'Sarah Ahmed',
    nameAr: 'سارة أحمد',
    email: 'sarah.ahmed@example.com',
    avatar: '/avatars/sarah.jpg',
    location: 'Amman',
    locationAr: 'عمان',
    country: 'Jordan',
    countryAr: 'الأردن',
    bio: 'Passionate educator with 5+ years of experience in community development and youth mentoring.',
    bioAr: 'مربية شغوفة مع أكثر من 5 سنوات من الخبرة في تطوير المجتمع وتوجيه الشباب.',
    skills: ['Teaching', 'Project Management', 'Public Speaking'],
    interests: ['Education', 'Youth Development', 'Community Development'],
    languages: ['Arabic', 'English', 'French'],
    availability: 'part-time',
    experience: 'expert',
    joinDate: '2023-03-15',
    completedOpportunities: 12,
    rating: 4.9,
    verified: true
  },
  {
    id: 'vol-2',
    name: 'Ahmad Hassan',
    nameAr: 'أحمد حسن',
    email: 'ahmad.hassan@example.com',
    avatar: '/avatars/ahmad.jpg',
    location: 'Beirut',
    locationAr: 'بيروت',
    country: 'Lebanon',
    countryAr: 'لبنان',
    bio: 'Environmental engineer dedicated to creating sustainable solutions for MENA communities.',
    bioAr: 'مهندس بيئي مكرس لإيجاد حلول مستدامة لمجتمعات المنطقة العربية.',
    skills: ['Environmental Science', 'Data Analysis', 'Research'],
    interests: ['Environment', 'Technology', 'Community Development'],
    languages: ['Arabic', 'English'],
    availability: 'weekends',
    experience: 'expert',
    joinDate: '2023-06-20',
    completedOpportunities: 8,
    rating: 4.7,
    verified: true
  },
  {
    id: 'vol-3',
    name: 'Fatima Al-Zahra',
    nameAr: 'فاطمة الزهراء',
    email: 'fatima.alzahra@example.com',
    avatar: '/avatars/fatima.jpg',
    location: 'Cairo',
    locationAr: 'القاهرة',
    country: 'Egypt',
    countryAr: 'مصر',
    bio: 'Medical student passionate about public health and healthcare accessibility in underserved areas.',
    bioAr: 'طالبة طب شغوفة بالصحة العامة وإمكانية الوصول إلى الرعاية الصحية في المناطق المحرومة.',
    skills: ['Healthcare', 'Counseling', 'Translation'],
    interests: ['Health', 'Community Development', 'Social Justice'],
    languages: ['Arabic', 'English'],
    availability: 'flexible',
    experience: 'intermediate',
    joinDate: '2023-09-10',
    completedOpportunities: 6,
    rating: 4.8,
    verified: true
  },
  {
    id: 'vol-4',
    name: 'Omar Al-Rashid',
    nameAr: 'عمر الراشد',
    email: 'omar.alrashid@example.com',
    avatar: '/avatars/omar.jpg',
    location: 'Dubai',
    locationAr: 'دبي',
    country: 'UAE',
    countryAr: 'الإمارات',
    bio: 'Software developer using technology to solve social problems and bridge the digital divide.',
    bioAr: 'مطور برمجيات يستخدم التكنولوجيا لحل المشاكل الاجتماعية وسد الفجوة الرقمية.',
    skills: ['Web Development', 'Mobile Apps', 'Data Analysis'],
    interests: ['Technology', 'Education', 'Youth Development'],
    languages: ['Arabic', 'English', 'Hindi'],
    availability: 'part-time',
    experience: 'expert',
    joinDate: '2023-02-28',
    completedOpportunities: 15,
    rating: 4.9,
    verified: true
  },
  {
    id: 'vol-5',
    name: 'Layla Al-Mansouri',
    nameAr: 'ليلى المنصوري',
    email: 'layla.almansouri@example.com',
    avatar: '/avatars/layla.jpg',
    location: 'Riyadh',
    locationAr: 'الرياض',
    country: 'Saudi Arabia',
    countryAr: 'السعودية',
    bio: 'Business consultant helping women entrepreneurs launch and scale their ventures.',
    bioAr: 'مستشارة أعمال تساعد رائدات الأعمال على إطلاق وتوسيع مشاريعهن.',
    skills: ['Business Development', 'Marketing', 'Fundraising'],
    interests: ['Women Empowerment', 'Education', 'Community Development'],
    languages: ['Arabic', 'English'],
    availability: 'weekends',
    experience: 'expert',
    joinDate: '2023-05-12',
    completedOpportunities: 9,
    rating: 4.6,
    verified: true
  }
];

// Sample Opportunities
export const SEED_OPPORTUNITIES: Opportunity[] = [
  {
    id: 'opp-1',
    title: 'English Tutor for Refugee Children',
    titleAr: 'مدرس إنجليزية للأطفال اللاجئين',
    description: 'Help refugee children improve their English skills through engaging one-on-one and group tutoring sessions. Make a lasting impact on their educational journey.',
    descriptionAr: 'ساعد الأطفال اللاجئين على تحسين مهاراتهم في اللغة الإنجليزية من خلال جلسات تدريس فردية وجماعية ممتعة. اترك تأثيراً دائماً على رحلتهم التعليمية.',
    organizationId: 'org-1',
    organizationName: 'Hope Foundation Jordan',
    organizationLogo: '/logos/hope-foundation.png',
    location: 'Amman',
    locationAr: 'عمان',
    country: 'Jordan',
    countryAr: 'الأردن',
    remote: false,
    causes: ['Education', 'Refugees'],
    skillsRequired: ['Teaching', 'English', 'Patience'],
    timeCommitment: '4 hours/week',
    duration: '6 months',
    urgency: 'high',
    volunteersNeeded: 8,
    volunteersApplied: 23,
    volunteersAccepted: 6,
    status: 'active',
    postedDate: '2024-01-15',
    applicationDeadline: '2024-02-15',
    startDate: '2024-02-20',
    requirements: [
      'Fluent in English and Arabic',
      'Experience working with children',
      'Available weekday afternoons',
      'Patient and empathetic personality'
    ],
    benefits: [
      'Professional development certificate',
      'Networking with education professionals',
      'Transportation allowance',
      'Impact measurement reports'
    ],
    images: ['/opportunities/english-tutoring-1.jpg', '/opportunities/english-tutoring-2.jpg'],
    featured: true,
    verified: true
  },
  {
    id: 'opp-2',
    title: 'Environmental Awareness Campaign Coordinator',
    titleAr: 'منسق حملة التوعية البيئية',
    description: 'Lead community outreach initiatives to raise environmental awareness and promote sustainable practices across Lebanese communities.',
    descriptionAr: 'قيادة مبادرات التوعية المجتمعية لرفع الوعي البيئي وتعزيز الممارسات المستدامة في المجتمعات اللبنانية.',
    organizationId: 'org-2',
    organizationName: 'Green Lebanon Initiative',
    organizationLogo: '/logos/green-lebanon.png',
    location: 'Beirut',
    locationAr: 'بيروت',
    country: 'Lebanon',
    countryAr: 'لبنان',
    remote: true,
    causes: ['Environment', 'Community Development'],
    skillsRequired: ['Social Media', 'Content Creation', 'Project Management'],
    timeCommitment: '6 hours/week',
    duration: '4 months',
    urgency: 'medium',
    volunteersNeeded: 3,
    volunteersApplied: 15,
    volunteersAccepted: 2,
    status: 'active',
    postedDate: '2024-01-10',
    applicationDeadline: '2024-02-10',
    startDate: '2024-02-15',
    requirements: [
      'Strong communication skills',
      'Social media experience',
      'Passion for environmental issues',
      'Available for weekend events'
    ],
    benefits: [
      'Leadership development training',
      'Environmental certification',
      'Networking opportunities',
      'Portfolio building projects'
    ],
    images: ['/opportunities/env-campaign-1.jpg', '/opportunities/env-campaign-2.jpg'],
    featured: true,
    verified: true
  },
  {
    id: 'opp-3',
    title: 'Community Health Educator',
    titleAr: 'مثقف صحي مجتمعي',
    description: 'Conduct health education workshops in underserved communities to promote preventive healthcare and wellness practices.',
    descriptionAr: 'إجراء ورش تثقيف صحي في المجتمعات المحرومة لتعزيز الرعاية الصحية الوقائية وممارسات العافية.',
    organizationId: 'org-3',
    organizationName: 'Cairo Medical Aid',
    organizationLogo: '/logos/cairo-medical.png',
    location: 'Cairo',
    locationAr: 'القاهرة',
    country: 'Egypt',
    countryAr: 'مصر',
    remote: false,
    causes: ['Health', 'Community Development'],
    skillsRequired: ['Public Health', 'Arabic', 'Presentation'],
    timeCommitment: '8 hours/week',
    duration: '12 months',
    urgency: 'high',
    volunteersNeeded: 5,
    volunteersApplied: 18,
    volunteersAccepted: 3,
    status: 'active',
    postedDate: '2024-01-08',
    applicationDeadline: '2024-02-08',
    startDate: '2024-02-12',
    requirements: [
      'Healthcare or related background',
      'Excellent Arabic communication',
      'Experience in community outreach',
      'Available for evening sessions'
    ],
    benefits: [
      'Medical training workshops',
      'Professional networking',
      'Health sector experience',
      'Community impact recognition'
    ],
    images: ['/opportunities/health-education-1.jpg', '/opportunities/health-education-2.jpg'],
    featured: false,
    verified: true
  }
];

// Utility functions for generating more seed data
export const generateRandomId = (prefix: string): string => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

export const getRandomItem = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

export const getRandomItems = <T>(array: T[], count: number): T[] => {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

export const generateRandomDate = (daysBack: number): string => {
  const date = new Date();
  date.setDate(date.getDate() - Math.floor(Math.random() * daysBack));
  return date.toISOString().split('T')[0];
};

// Comprehensive seed data object
export const SEED_DATA = {
  organizations: SEED_ORGANIZATIONS,
  volunteers: SEED_VOLUNTEERS,
  opportunities: SEED_OPPORTUNITIES,
  countries: MENA_COUNTRIES,
  cities: MAJOR_CITIES,
  causes: CAUSES,
  skills: SKILLS
};