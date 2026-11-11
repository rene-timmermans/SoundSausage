/* Independent LADSPA 1.1 / LV2 ABI fixture: paired mono, adjustable delay,
   and a portable LV2 property not represented by a control port. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef void* Handle;
typedef struct { const char* URI; void* data; } Feature;
typedef struct { void* handle; uint32_t (*map)(void*,const char*); } Map;
typedef struct { float* ports[5];float ring[64];unsigned pos;float hidden;Map* map; } Gain;
static void* create(void) { Gain* g=calloc(1,sizeof(Gain));if(g)g->hidden=1;return g; }
static void connect(Handle h,unsigned long port,float* data) { if(port<5)((Gain*)h)->ports[port]=data; }
static void activate(Handle h) { Gain* g=h;memset(g->ring,0,sizeof(g->ring));g->pos=0; }
static void run(Handle h,unsigned long count) {
 Gain* g=h;unsigned delay=(unsigned)(*g->ports[4]+.5f);if(delay>28)delay=28;
 *g->ports[3]=(float)delay;
 for(unsigned long i=0;i<count;++i) {
  float input=g->ports[0][i];g->ring[g->pos]=input;
  g->ports[1][i]=g->ring[(g->pos+64-delay)%64]*(*g->ports[2])*g->hidden;
  g->pos=(g->pos+1)%64;
 }
}
static void cleanup(Handle h) { free(h); }
typedef struct { int flags;float low,high; } Hint;
typedef struct Ladspa Ladspa;
struct Ladspa {
 unsigned long id;const char* label;int properties;const char* name;const char* maker;const char* copyright;
 unsigned long count;const int* ports;const char* const* names;const Hint* hints;void* implementation;
 Handle (*instantiate)(const Ladspa*,unsigned long);void (*connect_port)(Handle,unsigned long,float*);
 void (*activate)(Handle);void (*run)(Handle,unsigned long);void* run_adding;void* set_run_adding_gain;
 void (*deactivate)(Handle);void (*cleanup)(Handle);
};
static Handle ladspa_create(const Ladspa* d,unsigned long rate) { (void)d;(void)rate;return create(); }
static const int port_flags[]={9,10,5,6,5};
static const char* names[]={"Input","Output","Gain","_latency","Delay"};
static const Hint hints[]={{0,0,0},{0,0,0},{3|0xc0,0,2},{3|32,0,1024},{3|32|0x80,0,28}};
static const Ladspa ladspa={1900001,"test_gain_delay",0,"SoundSausage LADSPA fixture","SoundSausage","GPL-3.0-or-later",5,
 port_flags,names,hints,NULL,ladspa_create,connect,activate,run,NULL,NULL,NULL,cleanup};
const Ladspa* ladspa_descriptor(unsigned long index) { return index?NULL:&ladspa; }

typedef struct Lv2 Lv2;
struct Lv2 { const char* URI;Handle (*instantiate)(const Lv2*,double,const char*,const Feature* const*);
 void (*connect_port)(Handle,uint32_t,void*);void (*activate)(Handle);void (*run)(Handle,uint32_t);
 void (*deactivate)(Handle);void (*cleanup)(Handle);const void* (*extension_data)(const char*); };
static Handle lv2_create(const Lv2* d,double rate,const char* bundle,const Feature* const* features) {
 (void)d;(void)rate;(void)bundle;Gain* g=create();if(!g)return NULL;
 for(unsigned i=0;features&&features[i];++i)if(!strcmp(features[i]->URI,"http://lv2plug.in/ns/ext/urid#map"))g->map=features[i]->data;
 if(!g->map) { cleanup(g);return NULL; }return g;
}
static void lv2_connect(Handle h,uint32_t port,void* data) { connect(h,port,data); }
static void lv2_run(Handle h,uint32_t count) { run(h,count); }
typedef int (*Store)(Handle,uint32_t,const void*,size_t,uint32_t,uint32_t);
typedef const void* (*Retrieve)(Handle,uint32_t,size_t*,uint32_t*,uint32_t*);
typedef struct { int (*save)(Handle,Store,Handle,uint32_t,const Feature* const*);
 int (*restore)(Handle,Retrieve,Handle,uint32_t,const Feature* const*); } State;
static int save(Handle h,Store store,Handle context,uint32_t flags,const Feature* const* features) {
 (void)flags;(void)features;Gain* g=h;
 return store(context,g->map->map(g->map->handle,"urn:soundsausage:test:hidden"),&g->hidden,sizeof(float),
   g->map->map(g->map->handle,"http://lv2plug.in/ns/ext/atom#Float"),3);
}
static int restore(Handle h,Retrieve retrieve,Handle context,uint32_t flags,const Feature* const* features) {
 (void)flags;(void)features;Gain* g=h;size_t size;uint32_t type,stored_flags;
 const void* value=retrieve(context,g->map->map(g->map->handle,"urn:soundsausage:test:hidden"),&size,&type,&stored_flags);
 if(value) { if(size!=sizeof(float))return 2;memcpy(&g->hidden,value,size); }return 0;
}
static const State state={save,restore};
static const void* extension(const char* uri) { return !strcmp(uri,"http://lv2plug.in/ns/ext/state#interface")?&state:NULL; }
static const Lv2 lv2={"urn:soundsausage:test:lv2:gain",lv2_create,lv2_connect,activate,lv2_run,NULL,cleanup,extension};
const Lv2* lv2_descriptor(uint32_t index) { return index?NULL:&lv2; }
